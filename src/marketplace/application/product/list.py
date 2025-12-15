from dataclasses import dataclass
from decimal import Decimal

from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.product.product import Product
from marketplace.domain.entities.product.repository import ProductRepository


@dataclass(frozen=True, slots=True)
class ListProductsRequest:
    category_id: int | None = None
    min_price: Decimal | None = None
    max_price: Decimal | None = None
    is_active: bool = True
    limit: int = 20
    offset: int = 0


class ListProducts:
    def __init__(self, product_repository: ProductRepository) -> None:
        self._product_repository = product_repository

    async def __call__(self, filters: ListProductsRequest) -> list[Product]:
        return await self._product_repository.list(
            category_id=Identity(filters.category_id)
            if filters.category_id
            else None,
            min_price=filters.min_price,
            max_price=filters.max_price,
            is_active=filters.is_active,
            limit=filters.limit,
            offset=filters.offset,
        )
