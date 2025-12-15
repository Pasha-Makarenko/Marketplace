from dataclasses import dataclass

from marketplace.application.common.id_provider import IdProvider
from marketplace.application.common.transaction_manager import (
    TransactionManager,
)
from marketplace.application.product.shared import check_product_ownership
from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.product.repository import ProductRepository
from marketplace.domain.entities.seller.repository import SellerRepository
from marketplace.domain.exceptions import EntityNotFound


@dataclass(frozen=True, slots=True)
class DeleteProductRequest:
    product_id: int


class DeleteProduct:
    def __init__(
        self,
        product_repository: ProductRepository,
        seller_repository: SellerRepository,
        tr_manager: TransactionManager,
        id_provider: IdProvider,
    ):
        self._product_repository = product_repository
        self._seller_repository = seller_repository
        self._tr_manager = tr_manager
        self._id_provider = id_provider

    async def __call__(self, data: DeleteProductRequest) -> None:
        product = await self._product_repository.by_identity(
            Identity(_value=data.product_id)
        )

        if product is None:
            raise EntityNotFound(
                field_name="product",
                value=data.product_id,
            )

        user_id = await self._id_provider.get_current_user_id()
        await check_product_ownership(
            product, user_id, self._seller_repository
        )

        product.deactivate()

        await self._tr_manager.commit()
