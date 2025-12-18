from typing import TypedDict

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class CategoryStatsRow(TypedDict):
    id: int
    name: str
    product_count: int
    avg_price: float


class CategoryAnalyticsQuery:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_category_distribution(self) -> list[dict[str, object]]:
        stmt = text(
            """
            WITH category_stats AS (
                SELECT
                    c.category_id,
                    c.name,
                    COUNT(p.product_id) AS product_count,
                    COALESCE(AVG(p.price), 0) AS avg_price
                FROM categories c
                LEFT JOIN products p
                    ON p.category_id = c.category_id AND p.is_active = true
                GROUP BY c.category_id, c.name
            )
            SELECT COALESCE(
                json_agg(
                    json_build_object(
                        'id', cs.category_id,
                        'name', cs.name,
                        'product_count', cs.product_count,
                        'avg_price', cs.avg_price
                    )
                    ORDER BY cs.product_count DESC
                ),
                '[]'::json
            )
            FROM category_stats cs
            """
        )
        result = await self._session.scalar(stmt)
        return result or []
