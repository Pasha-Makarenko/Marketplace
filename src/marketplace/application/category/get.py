from dataclasses import dataclass

from marketplace.domain.entities.category.category import Category
from marketplace.domain.entities.category.repository import CategoryRepository
from marketplace.domain.entities.identity import Identity
from marketplace.domain.exceptions import EntityNotFound


@dataclass(frozen=True, slots=True)
class GetCategoryRequest:
    category_id: int


class GetCategory:
    def __init__(self, category_repository: CategoryRepository) -> None:
        self._category_repository = category_repository

    async def __call__(self, data: GetCategoryRequest) -> Category:
        category = await self._category_repository.by_identity(
            Identity(_value=data.category_id)
        )

        if category is None:
            raise EntityNotFound(
                field_name="category",
                value=data.category_id,
            )
        return category
