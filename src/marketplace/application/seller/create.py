from marketplace.application.common.transaction_manager import (
    TransactionManager,
)
from marketplace.domain.entities.seller.factory import (
    CreateSellerRequest,
    SellerFactory,
)
from marketplace.domain.entities.seller.repository import SellerRepository


class CreateSeller:
    def __init__(
        self,
        seller_factory: SellerFactory,
        seller_repository: SellerRepository,
        tr_manager: TransactionManager,
    ) -> None:
        self._seller_factory = seller_factory
        self._seller_repository = seller_repository
        self._tr_manager = tr_manager

    async def __call__(self, data: CreateSellerRequest) -> int:
        seller = await self._seller_factory.create(data=data)

        self._seller_repository.add(seller)
        await self._tr_manager.commit()

        return seller.identity.value
