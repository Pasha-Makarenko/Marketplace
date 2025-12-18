from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.seller.repository import SellerRepository
from marketplace.domain.entities.seller.seller import Seller
from marketplace.infrastructure.persistence.base_repo import Repository


class SQLSellerRepository(Repository[Seller], SellerRepository):
    model = Seller

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def by_identity(self, seller_id: Identity) -> Seller | None:
        return await self._session.get(self.model, seller_id.value)

    async def by_user_id(self, user_id: Identity) -> Seller | None:
        stmt = select(self.model).where(self.model.user_id == user_id)  # type: ignore
        return await self._session.scalar(stmt)

    async def list(self, limit: int = 20, offset: int = 0) -> list[Seller]:
        stmt = select(self.model).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def is_user_identity_unique(self, user_id: Identity) -> bool:
        stmt = select(self.model).where(self.model.user_id == user_id)  # type: ignore
        return (await self._session.scalar(stmt)) is None
