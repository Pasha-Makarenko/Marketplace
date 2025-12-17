from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class ProductAnalyticsQuery:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_top_rated_products(
        self, limit: int = 10
    ) -> list[dict[str, object]]:
        stmt = text(
            """
            WITH product_ratings AS (
                SELECT
                    p.product_id,
                    p.name,
                    p.price,
                    AVG(r.rating) AS avg_rating,
                    COUNT(r.review_id) AS review_count
                FROM products p
                LEFT JOIN reviews r ON r.product_id = p.product_id
                WHERE p.is_active = true
                GROUP BY p.product_id, p.name, p.price
            )
            SELECT COALESCE(
                json_agg(
                    json_build_object(
                        'id', pr.product_id,
                        'name', pr.name,
                        'price', pr.price,
                        'avg_rating', COALESCE(pr.avg_rating, 0),
                        'review_count', pr.review_count
                    )
                    ORDER BY pr.avg_rating DESC NULLS LAST,
                        pr.review_count DESC
                ),
                '[]'::json
            )
            FROM (
                SELECT * FROM product_ratings LIMIT :limit
            ) pr
            """
        )
        result = await self._session.scalar(stmt, {"limit": limit})
        return result or []

    async def get_low_stock_products(
        self, threshold: int = 5
    ) -> list[dict[str, object]]:
        stmt = text(
            """
            SELECT COALESCE(
                json_agg(
                    json_build_object(
                        'id', p.product_id,
                        'name', p.name,
                        'stock_quantity', p.stock_quantity,
                        'seller_id', p.owner_id
                    )
                    ORDER BY p.stock_quantity ASC
                ),
                '[]'::json
            )
            FROM products p
            WHERE p.stock_quantity <= :threshold AND p.is_active = true
            """
        )
        result = await self._session.scalar(stmt, {"threshold": threshold})
        return result or []
