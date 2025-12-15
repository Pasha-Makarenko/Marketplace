from marketplace.domain.entities.category.category import Category
from marketplace.domain.entities.category.repository import CategoryRepository


class ListCategories:
    def __init__(self, category_repository: CategoryRepository) -> None:
        self._category_repository = category_repository

    async def __call__(self) -> list[Category]:
        return await self._category_repository.list()
