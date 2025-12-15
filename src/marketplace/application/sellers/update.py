from dataclasses import dataclass

from marketplace.application.common.transaction_manager import (
    TransactionManager,
)
from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.seller.repository import SellerRepository
from marketplace.domain.exceptions import EntityNotFound


@dataclass(frozen=True, slots=True)
class UpdateSellerRequest:
    seller_id: int
    store_name: str | None
    contact_info: str | None
    return_policy: str | None
    delivery_terms: str | None


class UpdateSeller:
    def __init__(
        self,
        seller_repository: SellerRepository,
        tr_manager: TransactionManager,
    ):
        self._seller_repository = seller_repository
        self._tr_manager = tr_manager

    async def __call__(self, data: UpdateSellerRequest) -> None:
        seller = await self._seller_repository.by_identity(
            Identity(_value=data.seller_id)
        )

        if seller is None:
            raise EntityNotFound(
                field_name="seller",
                value=data.seller_id,
            )

        if data.store_name is not None:
            seller.set_store_name(data.store_name)

        if data.contact_info is not None:
            seller.set_contact_info(data.contact_info)

        if data.return_policy is not None:
            seller.set_return_policy(data.return_policy)

        if data.delivery_terms is not None:
            seller.set_delivery_terms(data.delivery_terms)

        await self._tr_manager.commit()
