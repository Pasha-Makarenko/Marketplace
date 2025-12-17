from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

from marketplace.application.common.transaction_manager import (
    TransactionManager,
)
from marketplace.domain.entities.category.category import Category
from marketplace.domain.entities.category.repository import CategoryRepository
from marketplace.domain.entities.identity import Identity
from marketplace.domain.exceptions import EntityNotFound


class CreateCategoryRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: Annotated[
        str, StringConstraints(strip_whitespace=True, max_length=30)
    ]
    parent_category_id: int | None = None


class CategoryFactory:
    def __init__(
        self,
        category_repository: CategoryRepository,
        transaction_manager: TransactionManager,
    ) -> None:
        self._category_repository = category_repository
        self._transaction_manager = transaction_manager

    async def create(self, data: CreateCategoryRequest) -> Category:
        if data.parent_category_id is not None:
            parent_category = await self._category_repository.by_identity(
                category_id=Identity(_value=data.parent_category_id),
            )

            if not parent_category:
                raise EntityNotFound(
                    field_name="parent_category_id",
                    value=data.parent_category_id,
                )

        parent_identity = (
            Identity(data.parent_category_id)
            if data.parent_category_id is not None
            else None
        )

        category = Category(
            identity=Identity(_value=None),
            name=data.name,
            parent_category_id=parent_identity,
        )

        self._category_repository.add(category)

        await self._transaction_manager.flush()

        return category
