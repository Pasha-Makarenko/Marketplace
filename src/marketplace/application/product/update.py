from dataclasses import dataclass
from decimal import Decimal

from marketplace.application.common.transaction_manager import (
    TransactionManager,
)
from marketplace.domain.entities.category.repository import CategoryRepository
from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.product.repository import ProductRepository
from marketplace.domain.exceptions import EntityNotFound


@dataclass(frozen=True, slots=True)
class UpdateProductRequest:
    product_id: int
    name: str | None = None
    description: str | None = None
    price: Decimal | None = None
    discount: int | None = None
    stock_quantity: int | None = None
    category_id: int | None = None


class UpdateProduct:
    def __init__(
        self,
        product_repository: ProductRepository,
        category_repository: CategoryRepository,
        tr_manager: TransactionManager,
    ) -> None:
        self._product_repository = product_repository
        self._category_repository = category_repository
        self._tr_manager = tr_manager

    async def __call__(self, data: UpdateProductRequest) -> None:
        product = await self._product_repository.by_identity(
            Identity(_value=data.product_id)
        )

        if product is None:
            raise EntityNotFound(
                field_name="product",
                value=data.product_id,
            )

        if data.name is not None:
            product.change_name(data.name)

        if data.description is not None:
            product.change_description(data.description)

        if data.price is not None:
            product.change_price(data.price)

        if data.discount is not None:
            product.change_discount(data.discount)

        if data.stock_quantity is not None:
            product.change_stock_quantity(data.stock_quantity)

        if data.category_id is not None:
            category_identity = Identity(data.category_id)
            category = await self._category_repository.by_identity(
                category_identity
            )
            if not category:
                raise EntityNotFound(
                    field_name="category_id",
                    value=data.category_id,
                )
            product.change_category(category_identity)

        await self._tr_manager.commit()
