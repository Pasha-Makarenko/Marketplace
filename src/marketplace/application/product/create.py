from marketplace.application.common.id_provider import IdProvider
from marketplace.application.common.transaction_manager import (
    TransactionManager,
)
from marketplace.domain.entities.product.factory import (
    CreateProductRequest,
    ProductFactory,
)
from marketplace.domain.entities.product.repository import ProductRepository


class CreateProduct:
    def __init__(
        self,
        product_factory: ProductFactory,
        product_repository: ProductRepository,
        tr_manager: TransactionManager,
        id_provider: IdProvider,
    ) -> None:
        self._product_factory = product_factory
        self._product_repository = product_repository
        self._tr_manager = tr_manager
        self._id_provider = id_provider

    async def __call__(self, data: CreateProductRequest) -> int:
        user_id = await self._id_provider.get_current_user_id()
        product = await self._product_factory.create(
            data=data, user_id=user_id
        )

        self._product_repository.add(product)
        await self._tr_manager.commit()

        return product.identity.value
