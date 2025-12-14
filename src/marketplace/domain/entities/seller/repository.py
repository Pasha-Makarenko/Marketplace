from abc import abstractmethod
from typing import Protocol

from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.seller.seller import Seller


class SellerRepository(Protocol):
    @abstractmethod
    async def by_identity(self, seller_id: Identity) -> Seller | None:
        raise NotImplementedError

    @abstractmethod
    async def is_user_identity_unique(self, user_id: Identity) -> bool:
        raise NotImplementedError

    @abstractmethod
    def add(self, seller: Seller) -> None:
        raise NotImplementedError
