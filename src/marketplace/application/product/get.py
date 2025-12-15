from dataclasses import dataclass

from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.product.product import Product
from marketplace.domain.entities.product.repository import ProductRepository
from marketplace.domain.exceptions import EntityNotFound


@dataclass(frozen=True, slots=True)
class GetProductRequest:
    product_id: int


class GetProduct:
    def __init__(self, product_repository: ProductRepository) -> None:
        self._product_repository = product_repository

    async def __call__(self, data: GetProductRequest) -> Product:
        product = await self._product_repository.by_identity(
            Identity(_value=data.product_id)
        )

        if product is None:
            raise EntityNotFound(
                field_name="product",
                value=data.product_id,
            )
        return product
