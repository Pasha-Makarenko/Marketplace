from dataclasses import dataclass

from marketplace.application.common.transaction_manager import (
    TransactionManager,
)
from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.seller.factory import (
    CreateSellerRequest,
    SellerFactory,
)
from marketplace.domain.entities.seller.repository import SellerRepository


@dataclass(frozen=True, slots=True)
class SellerCreationRequest:
    user_id: int
    store_name: str
    contact_info: str
    return_policy: str
    delivery_terms: str


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

    async def __call__(self, data: SellerCreationRequest) -> int:
        seller = await self._seller_factory.create(
            data=CreateSellerRequest(
                user_id=Identity(data.user_id),
                store_name=data.store_name,
                contact_info=data.contact_info,
                return_policy=data.return_policy,
                delivery_terms=data.delivery_terms,
            )
        )

        self._seller_repository.add(seller)

        await self._tr_manager.commit()

        return seller.identity.value
