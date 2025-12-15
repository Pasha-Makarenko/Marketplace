from dataclasses import dataclass

from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.seller.repository import SellerRepository
from marketplace.domain.entities.seller.seller import Seller
from marketplace.domain.exceptions import EntityNotFound


@dataclass(frozen=True, slots=True)
class GetSellerRequest:
    seller_id: int


class GetSeller:
    def __init__(self, seller_repository: SellerRepository) -> None:
        self._seller_repository = seller_repository

    async def __call__(self, data: GetSellerRequest) -> Seller:
        seller = await self._seller_repository.by_identity(
            Identity(_value=data.seller_id)
        )

        if seller is None:
            raise EntityNotFound(
                field_name="seller",
                value=data.seller_id,
            )
        return seller
