from marketplace.application.common.transaction_manager import (
    TransactionManager,
)
from marketplace.domain.entities.product.factory import (
    CreateProductRequest,
    ProductFactory,
)


class CreateProduct:
    def __init__(
        self,
        product_factory: ProductFactory,
        tr_manager: TransactionManager,
    ) -> None:
        self._product_factory = product_factory
        self._tr_manager = tr_manager

    async def __call__(self, data: CreateProductRequest) -> int:
        product = await self._product_factory.create(data=data)

        await self._tr_manager.commit()

        return product.identity.value
