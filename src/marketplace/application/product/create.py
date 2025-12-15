from dataclasses import dataclass
from decimal import Decimal

from marketplace.application.common.transaction_manager import (
    TransactionManager,
)
from marketplace.domain.entities.category.repository import CategoryRepository
from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.product.product import Product
from marketplace.domain.entities.product.repository import ProductRepository
from marketplace.domain.entities.seller.repository import SellerRepository
from marketplace.domain.exceptions import EntityNotFound


@dataclass(frozen=True, slots=True)
class ProductCreationRequest:
    name: str
    description: str | None
    price: Decimal
    discount: int
    stock_quantity: int
    owner_id: int
    category_id: int


class CreateProduct:
    def __init__(
        self,
        product_repository: ProductRepository,
        seller_repository: SellerRepository,
        category_repository: CategoryRepository,
        tr_manager: TransactionManager,
    ) -> None:
        self._product_repository = product_repository
        self._seller_repository = seller_repository
        self._category_repository = category_repository
        self._tr_manager = tr_manager

    async def __call__(self, data: ProductCreationRequest) -> int:
        owner_identity = Identity(data.owner_id)
        owner = await self._seller_repository.by_identity(owner_identity)
        if not owner:
            raise EntityNotFound(
                field_name="owner_id",
                value=data.owner_id,
            )

        category_identity = Identity(data.category_id)
        category = await self._category_repository.by_identity(
            category_identity
        )
        if not category:
            raise EntityNotFound(
                field_name="category_id",
                value=data.category_id,
            )

        product = Product(
            identity=Identity(_value=None),
            name=data.name,
            description=data.description,
            price=data.price,
            discount=data.discount,
            stock_quantity=data.stock_quantity,
            owner_id=owner_identity,
            category_id=category_identity,
        )

        self._product_repository.add(product)

        await self._tr_manager.commit()

        return product.identity.value
