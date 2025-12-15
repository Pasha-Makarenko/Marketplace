from dataclasses import dataclass

from marketplace.application.common.transaction_manager import (
    TransactionManager,
)
from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.seller.repository import SellerRepository
from marketplace.domain.exceptions import EntityNotFound


@dataclass(frozen=True, slots=True)
class DeleteSellerRequest:
    seller_id: int


class DeleteSeller:
    def __init__(
        self,
        seller_repository: SellerRepository,
        tr_manager: TransactionManager,
    ):
        self._seller_repository = seller_repository
        self._tr_manager = tr_manager

    async def __call__(self, data: DeleteSellerRequest) -> None:
        seller = await self._seller_repository.by_identity(
            Identity(_value=data.seller_id)
        )

        if seller is None:
            raise EntityNotFound(
                field_name="seller",
                value=data.seller_id,
            )

        seller.inactivate()

        await self._tr_manager.commit()
