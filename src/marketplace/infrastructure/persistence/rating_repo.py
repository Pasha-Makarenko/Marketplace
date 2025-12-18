from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.rating.rating import Rating
from marketplace.domain.entities.rating.repository import RatingRepository
from marketplace.infrastructure.persistence.base_repo import Repository
from marketplace.infrastructure.persistence.tables.ratings import ratings_table


class SQLRatingRepository(Repository[Rating], RatingRepository):
    model = Rating

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def by_identity(self, rating_id: Identity) -> Rating | None:
        return await self._session.get(self.model, rating_id.value)

    async def list_by_product(
        self, product_id: Identity, limit: int, offset: int
    ) -> list[Rating]:
        query = (
            select(self.model)
            .where(ratings_table.c.product_id_val == product_id.value)
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def get_average_for_product(self, product_id: Identity) -> float:
        query = select(func.avg(ratings_table.c.value)).where(
            ratings_table.c.product_id_val == product_id.value
        )
        result = await self._session.execute(query)
        avg_value = result.scalar()
        return float(avg_value) if avg_value is not None else 0.0

    async def get_rating_distribution(
        self, product_id: Identity
    ) -> dict[int, int]:
        query = (
            select(
                ratings_table.c.value, func.count(ratings_table.c.rating_id)
            )
            .where(ratings_table.c.product_id_val == product_id.value)
            .group_by(ratings_table.c.value)
        )
        result = await self._session.execute(query)
        distribution = {i: 0 for i in range(1, 6)}
        for rating_value, count in result.all():
            distribution[rating_value] = count
        return distribution
