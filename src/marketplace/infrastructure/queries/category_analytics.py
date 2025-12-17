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
            SELECT COALESCE(
                json_agg(
                    json_build_object(
                        'id', c.category_id,
                        'name', c.name,
                        'product_count', COUNT(p.product_id),
                        'avg_price', COALESCE(AVG(p.price), 0)
                    )
                    ORDER BY COUNT(p.product_id) DESC
                ),
                '[]'::json
            )
            FROM categories c
            LEFT JOIN products p
                ON p.category_id = c.category_id AND p.is_active = true
            GROUP BY c.category_id, c.name
            """
        )
        result = await self._session.scalar(stmt)
        return result or []
