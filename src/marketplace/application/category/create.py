from marketplace.application.common.transaction_manager import (
    TransactionManager,
)
from marketplace.domain.entities.category.factory import (
    CategoryFactory,
    CreateCategoryRequest,
)
from marketplace.domain.entities.category.repository import CategoryRepository


class CreateCategory:
    def __init__(
        self,
        category_factory: CategoryFactory,
        category_repository: CategoryRepository,
        tr_manager: TransactionManager,
    ) -> None:
        self._category_factory = category_factory
        self._category_repository = category_repository
        self._tr_manager = tr_manager

    async def __call__(self, data: CreateCategoryRequest) -> int:
        category = await self._category_factory.create(data=data)

        self._category_repository.add(category)
        await self._tr_manager.commit()

        return category.identity.value
