from dataclasses import dataclass

from marketplace.application.common.transaction_manager import (
    TransactionManager,
)
from marketplace.domain.entities.category.repository import CategoryRepository
from marketplace.domain.entities.identity import Identity
from marketplace.domain.exceptions import EntityNotFound


@dataclass(frozen=True, slots=True)
class DeleteCategoryRequest:
    category_id: int


class DeleteCategory:
    def __init__(
        self,
        category_repository: CategoryRepository,
        tr_manager: TransactionManager,
    ):
        self._category_repository = category_repository
        self._tr_manager = tr_manager

    async def __call__(self, data: DeleteCategoryRequest) -> None:
        category = await self._category_repository.by_identity(
            Identity(_value=data.category_id)
        )

        if category is None:
            raise EntityNotFound(
                field_name="category_id",
                value=data.category_id,
            )

        await self._category_repository.remove(category)

        await self._tr_manager.commit()
