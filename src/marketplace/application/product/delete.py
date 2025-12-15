from dataclasses import dataclass

from marketplace.application.common.transaction_manager import (
    TransactionManager,
)
from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.product.repository import ProductRepository
from marketplace.domain.exceptions import EntityNotFound


@dataclass(frozen=True, slots=True)
class DeleteProductRequest:
    product_id: int


class DeleteProduct:
    def __init__(
        self,
        product_repository: ProductRepository,
        tr_manager: TransactionManager,
    ):
        self._product_repository = product_repository
        self._tr_manager = tr_manager

    async def __call__(self, data: DeleteProductRequest) -> None:
        product = await self._product_repository.by_identity(
            Identity(_value=data.product_id)
        )

        if product is None:
            raise EntityNotFound(
                field_name="product",
                value=data.product_id,
            )

        self._product_repository.remove(product)

        await self._tr_manager.commit()
