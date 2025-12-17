from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from marketplace.domain.entities.category.repository import CategoryRepository
from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.product.product import Product
from marketplace.domain.entities.product.repository import ProductRepository
from marketplace.domain.entities.seller.repository import SellerRepository
from marketplace.domain.exceptions import DomainError, EntityNotFound


class CreateProductRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: Annotated[
        str, StringConstraints(strip_whitespace=True, max_length=255)
    ]
    description: str | None = None
    price: Annotated[Decimal, Field(ge=0)]
    discount: Annotated[int, Field(ge=0, le=100)] = 0
    stock_quantity: Annotated[int, Field(ge=0)]
    category_id: int


class ProductFactory:
    def __init__(
        self,
        product_repository: ProductRepository,
        seller_repository: SellerRepository,
        category_repository: CategoryRepository,
    ) -> None:
        self._product_repository = product_repository
        self._seller_repository = seller_repository
        self._category_repository = category_repository

    async def create(
        self, data: CreateProductRequest, user_id: int
    ) -> Product:
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

        return product
