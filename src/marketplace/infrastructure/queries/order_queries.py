from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import TypedDict

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from marketplace.application.common.id_provider import IdProvider


class UserOrderRow(TypedDict):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    total_amount: float | str | int
    items_count: int


class DailyRevenueRow(TypedDict):
    day: str
    revenue: float
    orders: int


class UserOrdersQuery:
    def __init__(self, session: AsyncSession, id_provider: IdProvider) -> None:
        self._session = session
        self._id_provider = id_provider

    async def fetch(self) -> list[dict[str, object]]:
        user_id = await self._id_provider.get_current_user_id()
        stmt = text(
            """
            WITH order_totals AS (
                SELECT
                    o.order_id,
                    o.status,
                    o.created_at,
                    o.updated_at,
                    COALESCE(
                        SUM(oi.price_at_purchase * oi.quantity),
                        0
                    ) AS total_amount,
                    COALESCE(SUM(oi.quantity), 0) AS items_count
                FROM orders o
                LEFT JOIN order_items oi ON oi.order_id = o.order_id
                WHERE o.user_id = :user_id
                GROUP BY o.order_id, o.status, o.created_at, o.updated_at
            )
            SELECT COALESCE(
                json_agg(
                    json_build_object(
                        'id', ot.order_id,
                        'status', ot.status,
                        'created_at', ot.created_at,
                        'updated_at', ot.updated_at,
                        'total_amount', ot.total_amount,
                        'items_count', ot.items_count
                    )
                    ORDER BY ot.created_at DESC
                ),
                '[]'::json
            ) AS orders_json
            FROM order_totals ot
            """
        )
        result = await self._session.scalar(stmt, {"user_id": user_id})
        return result or []


class OrderStatusStatsQuery:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def fetch(self) -> dict[str, int]:
        stmt = text(
            """
            SELECT COALESCE(json_object_agg(status, cnt), '{}'::json) AS stats
            FROM (
                SELECT status, COUNT(*) AS cnt
                FROM orders
                GROUP BY status
            ) s
            """
        )
        result = await self._session.scalar(stmt)
        return result or {}


class DailyRevenueQuery:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def fetch(self, days: int = 30) -> list[dict[str, object]]:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        stmt = text(
            """
            WITH daily AS (
                SELECT
                    DATE_TRUNC('day', o.paid_at) AS day,
                    SUM(oi.price_at_purchase * oi.quantity) AS revenue,
                    COUNT(DISTINCT o.order_id) AS orders
                FROM orders o
                JOIN order_items oi ON oi.order_id = o.order_id
                WHERE o.paid_at IS NOT NULL
                  AND o.paid_at >= :since
                GROUP BY DATE_TRUNC('day', o.paid_at)
            )
            SELECT COALESCE(
                json_agg(
                    json_build_object(
                        'day', to_char(day, 'YYYY-MM-DD'),
                        'revenue', revenue,
                        'orders', orders
                    )
                    ORDER BY day DESC
                ),
                '[]'::json
            ) AS revenue_json
            FROM daily
            """
        )
        result = await self._session.scalar(stmt, {"since": since})
        return result or []
