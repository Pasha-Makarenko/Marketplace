from dataclasses import dataclass

from marketplace.application.common.transaction_manager import (
    TransactionManager,
)
from marketplace.domain.entities.category.category import Category
from marketplace.domain.entities.category.repository import CategoryRepository
from marketplace.domain.entities.identity import Identity
from marketplace.domain.exceptions import EntityNotFound


@dataclass(frozen=True, slots=True)
class CategoryCreationRequest:
    name: str
    parent_category_id: int | None = None


class CreateCategory:
    def __init__(
        self,
        category_repository: CategoryRepository,
        tr_manager: TransactionManager,
    ) -> None:
        self._category_repository = category_repository
        self._tr_manager = tr_manager

    async def __call__(self, data: CategoryCreationRequest) -> int:
        if data.parent_category_id is not None:
            parent_category = await self._category_repository.by_identity(
                Identity(_value=data.parent_category_id)
            )

            if not parent_category:
                raise EntityNotFound(
                    field_name="parent_category_id",
                    value=data.parent_category_id,
                )

        category = Category(
            identity=Identity(_value=None),
            name=data.name,
            parent_category_id=Identity(_value=data.parent_category_id),
        )

        self._category_repository.add(category)

        await self._tr_manager.commit()

        return category.identity.value
