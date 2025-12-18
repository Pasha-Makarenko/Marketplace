from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.product.product import Product
from marketplace.domain.entities.product.repository import ProductRepository
from marketplace.infrastructure.persistence.base_repo import Repository


class SQLProductRepository(Repository[Product], ProductRepository):
    model = Product

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def by_identity(self, product_id: Identity) -> Product | None:
        return await self._session.get(self.model, product_id.value)

    async def list_by_seller(self, seller_id: Identity) -> list[Product]:
        stmt = select(self.model).where(
            self.model.owner_id.value == seller_id.value  # type: ignore
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_category(self, category_id: Identity) -> list[Product]:
        stmt = select(self.model).where(
            self.model.category_id.value == category_id.value  # type: ignore
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def list(
        self,
        category_id: Identity | None = None,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        is_active: bool = True,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Product]:
        stmt = select(self.model).where(self.model.is_active == is_active)  # type: ignore

        if category_id:
            stmt = stmt.where(
                self.model.category_id.value == category_id.value  # type: ignore
            )
        if min_price is not None:
            stmt = stmt.where(self.model.price >= min_price)  # type: ignore
        if max_price is not None:
            stmt = stmt.where(self.model.price <= max_price)  # type: ignore

        stmt = stmt.limit(limit).offset(offset).order_by(self.model.identity)  # type: ignore
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def remove(self, product: Product) -> None:
        await self._session.delete(self.model)
