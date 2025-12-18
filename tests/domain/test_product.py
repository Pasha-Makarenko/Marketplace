from datetime import datetime, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from marketplace.application.common.id_provider import IdProvider
from marketplace.application.common.transaction_manager import (
    TransactionManager,
)
from marketplace.domain.entities.category.category import Category
from marketplace.domain.entities.category.repository import CategoryRepository
from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.product.factory import (
    CreateProductRequest,
    ProductFactory,
)
from marketplace.domain.entities.product.product import Product
from marketplace.domain.entities.product.repository import ProductRepository
from marketplace.domain.entities.seller.repository import SellerRepository
from marketplace.domain.entities.seller.seller import Seller
from marketplace.domain.entities.user.user import User
from marketplace.domain.entities.user.value_objects import Phone
from marketplace.domain.exceptions import DomainError, EntityNotFound

# --- Mocks ---


class FakeTransactionManager(TransactionManager):
    async def commit(self) -> None:  # type: ignore[override]
        return None

    async def flush(self) -> None:  # type: ignore[override]
        return None


class FakeIdProvider(IdProvider):
    def __init__(self, user_id: int) -> None:
        self.user_id = user_id

    async def get_current_user_id(self) -> int:
        return self.user_id

    async def get_user(self) -> User:
        return User(
            identity=Identity(self.user_id),
            first_name="Test",
            last_name="User",
            email=f"test{self.user_id}@example.com",
            hashed_password="hash",
            phone=Phone("+1234567890"),
            registered_at=datetime.now(timezone.utc),
        )


class FakeProductRepository(ProductRepository):
    def __init__(self) -> None:
        self._products: dict[int, Product] = {}
        self._seq = 1

    async def by_identity(self, product_id: Identity) -> Product | None:  # type: ignore[override]
        return self._products.get(product_id.value or -1)

    async def list_by_seller(self, seller_id: Identity) -> list[Product]:  # type: ignore[override]
        return [
            p
            for p in self._products.values()
            if p.owner_id.value == seller_id.value
        ]

    async def list_by_category(self, category_id: Identity) -> list[Product]:  # type: ignore[override]
        return [
            p
            for p in self._products.values()
            if p.category_id.value == category_id.value
        ]

    async def list(  # type: ignore[override]
        self,
        category_id: Identity | None = None,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        is_active: bool = True,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Product]:
        return list(self._products.values())[offset : offset + limit]

    def add(self, product: Product) -> None:  # type: ignore[override]
        if product.identity._value is None:
            new_id = self._seq
            self._seq += 1
            object.__setattr__(product, "identity", Identity(_value=new_id))
        self._products[product.identity.value] = product

    async def remove(self, product: Product) -> None:  # type: ignore[override]
        if product.identity.value in self._products:
            del self._products[product.identity.value]


class FakeSellerRepository(SellerRepository):
    def __init__(self) -> None:
        self._sellers: dict[int, Seller] = {}

    async def by_identity(self, seller_id: Identity) -> Seller | None:  # type: ignore[override]
        return self._sellers.get(seller_id.value or -1)

    async def by_user_id(self, user_id: int) -> Seller | None:  # type: ignore[override]
        for seller in self._sellers.values():
            if seller.user_id.value == user_id:
                return seller
        return None

    async def list(self, limit: int = 20, offset: int = 0) -> list[Seller]:  # type: ignore[override]
        return list(self._sellers.values())[offset : offset + limit]

    async def is_user_identity_unique(self, user_id: Identity) -> bool:  # type: ignore[override]
        return True

    def add(self, seller: Seller) -> None:  # type: ignore[override]
        self._sellers[seller.identity.value] = seller


class FakeCategoryRepository(CategoryRepository):
    def __init__(self) -> None:
        self._categories: dict[int, Category] = {}

    async def by_identity(self, category_id: Identity) -> Category | None:  # type: ignore[override]
        return self._categories.get(category_id.value or -1)

    async def list(self) -> list[Category]:  # type: ignore[override]
        return list(self._categories.values())

    def add(self, category: Category) -> None:  # type: ignore[override]
        self._categories[category.identity.value] = category

    async def remove(self, category: Category) -> None:  # type: ignore[override]
        pass


def make_seller(seller_id: int, user_id: int) -> Seller:
    return Seller(
        identity=Identity(seller_id),
        user_id=Identity(user_id),
        store_name="Test Store",
        store_logs=None,
        contact_info="Contact",
        return_policy="Policy",
        delivery_terms="Terms",
        is_active=True,
    )


def make_category(category_id: int, name: str) -> Category:
    return Category(
        identity=Identity(category_id), name=name, parent_category_id=None
    )


def make_product(product_id: int = 1) -> Product:
    return Product(
        identity=Identity(product_id),
        name="Test Product",
        description="Description",
        price=Decimal("100.00"),
        discount=0,
        stock_quantity=10,
        owner_id=Identity(1),
        category_id=Identity(1),
        is_active=True,
    )


# --- Entity Tests ---


def test_change_name_success() -> None:
    product = make_product()
    product.change_name("New Name")
    assert product.name == "New Name"


def test_change_name_empty_raises_error() -> None:
    product = make_product()
    with pytest.raises(DomainError, match="Product name cannot be empty."):
        product.change_name("")


def test_change_description_updates_value() -> None:
    product = make_product()
    product.change_description("New Description")
    assert product.description == "New Description"


def test_change_price_success() -> None:
    product = make_product()
    product.change_price(Decimal("50.00"))
    assert product.price == Decimal("50.00")


def test_change_price_negative_raises_error() -> None:
    product = make_product()
    with pytest.raises(DomainError, match="Price cannot be negative."):
        product.change_price(Decimal("-1.00"))


def test_change_discount_success() -> None:
    product = make_product()
    product.change_discount(20)
    assert product.discount == 20


def test_change_discount_invalid_raises_error() -> None:
    product = make_product()
    with pytest.raises(
        DomainError, match="Discount must be between 0 and 100."
    ):
        product.change_discount(101)
    with pytest.raises(
        DomainError, match="Discount must be between 0 and 100."
    ):
        product.change_discount(-1)


def test_change_stock_quantity_success() -> None:
    product = make_product()
    product.change_stock_quantity(50)
    assert product.stock_quantity == 50


def test_change_stock_quantity_negative_raises_error() -> None:
    product = make_product()
    with pytest.raises(
        DomainError, match="Stock quantity cannot be negative."
    ):
        product.change_stock_quantity(-5)


def test_change_category_updates_value() -> None:
    product = make_product()
    product.change_category(Identity(2))
    assert product.category_id.value == 2


def test_deactivate_sets_is_active_false() -> None:
    product = make_product()
    assert product.is_active is True
    product.deactivate()
    assert product.is_active is False


def test_activate_sets_is_active_true() -> None:
    product = make_product()
    product.deactivate()
    assert product.is_active is False
    product.activate()
    assert product.is_active is True


# --- Request Validation Tests ---


def test_create_product_request_valid() -> None:
    req = CreateProductRequest(
        name="Valid Product",
        price=Decimal("10.00"),
        stock_quantity=5,
        category_id=1,
    )
    assert req.name == "Valid Product"
    assert req.price == Decimal("10.00")
    assert req.stock_quantity == 5


def test_create_product_request_name_stripped() -> None:
    req = CreateProductRequest(
        name="  Product  ",
        price=Decimal("10.00"),
        stock_quantity=5,
        category_id=1,
    )
    assert req.name == "Product"


def test_create_product_request_invalid_price() -> None:
    with pytest.raises(ValidationError):
        CreateProductRequest(
            name="Product",
            price=Decimal("-10.00"),
            stock_quantity=5,
            category_id=1,
        )


def test_create_product_request_invalid_discount() -> None:
    with pytest.raises(ValidationError):
        CreateProductRequest(
            name="Product",
            price=Decimal("10.00"),
            discount=110,
            stock_quantity=5,
            category_id=1,
        )


def test_create_product_request_invalid_stock() -> None:
    with pytest.raises(ValidationError):
        CreateProductRequest(
            name="Product",
            price=Decimal("10.00"),
            stock_quantity=-1,
            category_id=1,
        )


# --- Factory Tests ---


@pytest.mark.asyncio
async def test_create_product_success() -> None:
    product_repo = FakeProductRepository()
    seller_repo = FakeSellerRepository()
    category_repo = FakeCategoryRepository()

    # Setup seller and category
    seller = make_seller(1, 1)  # seller_id=1, user_id=1
    seller_repo.add(seller)
    category = make_category(10, "Electronics")
    category_repo.add(category)

    factory = ProductFactory(product_repo, seller_repo, category_repo)

    req = CreateProductRequest(
        name="Smartphone",
        description="A smart phone",
        price=Decimal("999.99"),
        discount=0,
        stock_quantity=10,
        category_id=10,
    )

    product = await factory.create(req, user_id=1)

    assert product.name == "Smartphone"
    assert product.owner_id.value == 1  # Seller ID
    assert product.category_id.value == 10


@pytest.mark.asyncio
async def test_create_product_not_seller() -> None:
    product_repo = FakeProductRepository()
    seller_repo = FakeSellerRepository()
    category_repo = FakeCategoryRepository()

    factory = ProductFactory(product_repo, seller_repo, category_repo)

    req = CreateProductRequest(
        name="Smartphone",
        description="A smart phone",
        price=Decimal("999.99"),
        discount=0,
        stock_quantity=10,
        category_id=10,
    )

    with pytest.raises(DomainError, match="User is not a seller"):
        await factory.create(req, user_id=2)


@pytest.mark.asyncio
async def test_create_product_category_not_found() -> None:
    product_repo = FakeProductRepository()
    seller_repo = FakeSellerRepository()
    category_repo = FakeCategoryRepository()

    # Setup seller only
    seller = make_seller(1, 1)
    seller_repo.add(seller)

    factory = ProductFactory(product_repo, seller_repo, category_repo)

    req = CreateProductRequest(
        name="Smartphone",
        description="A smart phone",
        price=Decimal("999.99"),
        discount=0,
        stock_quantity=10,
        category_id=999,  # Category does not exist
    )

    with pytest.raises(EntityNotFound):
        await factory.create(req, user_id=1)
