from dataclasses import dataclass

from marketplace.application.common.transaction_manager import (
    TransactionManager,
)
from marketplace.domain.entities.category.repository import CategoryRepository
from marketplace.domain.entities.identity import Identity
from marketplace.domain.exceptions import EntityNotFound


@dataclass(frozen=True, slots=True)
class UpdateCategoryRequest:
    category_id: int
    name: str | None
    parent_category_id: int | None


class UpdateSeller:
    def __init__(
        self,
        category_repository: CategoryRepository,
        tr_manager: TransactionManager,
    ):
        self._category_repository = category_repository
        self._tr_manager = tr_manager

    async def __call__(self, data: UpdateCategoryRequest) -> None:
        category = await self._category_repository.by_identity(
            Identity(_value=data.category_id)
        )

        if category is None:
            raise EntityNotFound(
                field_name="category_id",
                value=data.category_id,
            )

        if data.name is not None:
            category.rename(data.name)

        if data.parent_category_id is not None:
            category.set_parent(Identity(_value=data.parent_category_id))

        await self._tr_manager.commit()
