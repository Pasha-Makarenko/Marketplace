from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.review.repository import ReviewRepository
from marketplace.domain.entities.review.review import Review
from marketplace.infrastructure.persistence.base_repo import Repository


class SQLReviewRepository(Repository[Review], ReviewRepository):
    model = Review

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def by_identity(self, review_id: Identity) -> Review | None:
        return await self._session.get(self.model, review_id.value)

    async def list_by_product(
        self, product_id: Identity, limit: int, offset: int
    ) -> list[Review]:
        query = (
            select(self.model)
            .where(self.model.product_id == product_id)  # type: ignore
            .limit(limit)
            .offset(offset)
            .order_by(self.model.created_at.desc())  # type: ignore
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def get_recent_reviews(self, limit: int) -> list[Review]:
        query = (
            select(self.model)
            .limit(limit)
            .order_by(self.model.created_at.desc())  # type: ignore
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())
