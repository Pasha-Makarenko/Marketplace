from dataclasses import dataclass

from marketplace.domain.entities.seller.repository import SellerRepository
from marketplace.domain.entities.seller.seller import Seller


@dataclass(frozen=True, slots=True)
class ListSellersRequest:
    limit: int = 20
    offset: int = 0


class ListSellers:
    def __init__(self, seller_repository: SellerRepository) -> None:
        self._seller_repository = seller_repository

    async def __call__(self, filters: ListSellersRequest) -> list[Seller]:
        return await self._seller_repository.list(
            limit=filters.limit,
            offset=filters.offset,
        )
