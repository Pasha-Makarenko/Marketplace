from dataclasses import dataclass
from decimal import Decimal

from marketplace.application.common.id_provider import IdProvider
from marketplace.application.common.transaction_manager import (
    TransactionManager,
)
from marketplace.domain.entities.category.repository import CategoryRepository
from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.product.product import Product
from marketplace.domain.entities.product.repository import ProductRepository
from marketplace.domain.entities.seller.repository import SellerRepository
from marketplace.domain.exceptions import DomainError, EntityNotFound


@dataclass(frozen=True, slots=True)
class ProductCreationRequest:
    name: str
    description: str | None
    price: Decimal
    discount: int
    stock_quantity: int
    category_id: int


class CreateProduct:
    def __init__(
        self,
        product_repository: ProductRepository,
        seller_repository: SellerRepository,
        category_repository: CategoryRepository,
        tr_manager: TransactionManager,
        id_provider: IdProvider,
    ) -> None:
        self._product_repository = product_repository
        self._seller_repository = seller_repository
        self._category_repository = category_repository
        self._tr_manager = tr_manager
        self._id_provider = id_provider

    async def __call__(self, data: ProductCreationRequest) -> int:
        user_id = await self._id_provider.get_current_user_id()
        owner = await self._seller_repository.by_user_id(user_id)
        if not owner:
            raise DomainError("User is not a seller.")

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
            owner_id=owner.identity,
            category_id=category_identity,
            is_active=True,
        )

        self._product_repository.add(product)

        await self._tr_manager.commit()

        return product.identity.value
