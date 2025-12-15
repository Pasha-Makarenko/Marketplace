from sqlalchemy.ext.asyncio import AsyncSession

from marketplace.domain.entities.category.category import Category
from marketplace.domain.entities.category.repository import CategoryRepository
from marketplace.domain.entities.identity import Identity
from marketplace.infrastructure.persistence.base_repo import Repository


class SQLCategoryRepository(Repository[Category], CategoryRepository):
    model = Category

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def by_identity(self, category_id: Identity) -> Category | None:
        return await self._session.get(self.model, category_id.value)

    async def remove(self, category: Category) -> None:
        await self._session.delete(category)
