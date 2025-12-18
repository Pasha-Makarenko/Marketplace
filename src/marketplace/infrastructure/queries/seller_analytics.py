from typing import TypedDict

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class SellerStatsRow(TypedDict):
    id: int
    store_name: str
    total_products: int
    average_rating: float
    total_reviews: int


class SellerAnalyticsQuery:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_top_sellers(
        self, limit: int = 10
    ) -> list[dict[str, object]]:
        stmt = text(
            """
            WITH seller_stats AS (
                SELECT
                    s.seller_id,
                    s.store_name,
                    COUNT(DISTINCT p.product_id) AS total_products,
                    AVG(rat.value) AS avg_seller_rating,
                    COUNT(rat.rating_id) AS total_ratings
                FROM seller_profiles s
                LEFT JOIN products p
                    ON p.owner_id = s.seller_id AND p.is_active = true
                LEFT JOIN ratings rat ON rat.product_id = p.product_id
                WHERE s.is_active = true
                GROUP BY s.seller_id, s.store_name
            )
            SELECT COALESCE(
                json_agg(
                    json_build_object(
                        'id', ss.seller_id,
                        'store_name', ss.store_name,
                        'total_products', ss.total_products,
                        'average_rating', COALESCE(ss.avg_seller_rating, 0),
                        'total_ratings', ss.total_ratings
                    )
                    ORDER BY ss.avg_seller_rating DESC NULLS LAST
                ),
                '[]'::json
            )
            FROM (
                SELECT * FROM seller_stats LIMIT :limit
            ) ss
            """
        )
        result = await self._session.scalar(stmt, {"limit": limit})
        return result or []
