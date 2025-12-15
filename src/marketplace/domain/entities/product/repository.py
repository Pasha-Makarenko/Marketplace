from abc import abstractmethod
from decimal import Decimal
from typing import Protocol

from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.product.product import Product


class ProductRepository(Protocol):
    @abstractmethod
    async def by_identity(self, product_id: Identity) -> Product | None:
        raise NotImplementedError

    @abstractmethod
    async def list_by_seller(self, seller_id: Identity) -> list[Product]:
        raise NotImplementedError

    @abstractmethod
    async def list_by_category(self, category_id: Identity) -> list[Product]:
        raise NotImplementedError

    @abstractmethod
    async def list(
        self,
        category_id: Identity | None = None,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        is_active: bool = True,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Product]:
        raise NotImplementedError

    @abstractmethod
    def add(self, product: Product) -> None:
        raise NotImplementedError

    @abstractmethod
    async def remove(self, product: Product) -> None:
        raise NotImplementedError
