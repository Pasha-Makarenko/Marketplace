from marketplace.application.common.transaction_manager import (
    TransactionManager,
)
from marketplace.domain.entities.seller.factory import (
    CreateSellerRequest,
    SellerFactory,
)


class CreateSeller:
    def __init__(
        self,
        seller_factory: SellerFactory,
        tr_manager: TransactionManager,
    ) -> None:
        self._seller_factory = seller_factory
        self._tr_manager = tr_manager

    async def __call__(self, data: CreateSellerRequest) -> int:
        seller = await self._seller_factory.create(data=data)

        await self._tr_manager.commit()

        return seller.identity.value
