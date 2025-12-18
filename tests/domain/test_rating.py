import pytest
from pydantic import ValidationError

from marketplace.application.common.id_provider import IdProvider
from marketplace.application.common.transaction_manager import (
    TransactionManager,
)
from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.product.product import Product
from marketplace.domain.entities.product.repository import ProductRepository
from marketplace.domain.entities.rating.factory import (
    CreateRatingRequest,
    RatingFactory,
)
from marketplace.domain.entities.rating.rating import Rating
from marketplace.domain.entities.rating.repository import RatingRepository
from marketplace.domain.entities.user.user import User
from marketplace.domain.exceptions import EntityNotFound

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
        raise NotImplementedError


class FakeRatingRepository(RatingRepository):
    def __init__(self) -> None:
        self._ratings: dict[int, Rating] = {}
        self._seq = 1

    def add(self, rating: Rating) -> None:  # type: ignore[override]
        if rating.identity._value is None:
            new_id = self._seq
            self._seq += 1
            object.__setattr__(rating, "identity", Identity(_value=new_id))
        self._ratings[rating.identity.value] = rating

    async def by_identity(self, rating_id: Identity) -> Rating | None:  # type: ignore[override]
        return self._ratings.get(rating_id.value or -1)

    async def list_by_product(  # type: ignore[override]
        self, product_id: Identity, limit: int, offset: int
    ) -> list[Rating]:
        return [
            r
            for r in self._ratings.values()
            if r.product_id.value == product_id.value
        ]

    async def get_average_for_product(self, product_id: Identity) -> float:  # type: ignore[override]
        ratings = [
            r.value
            for r in self._ratings.values()
            if r.product_id.value == product_id.value
        ]
        if not ratings:
            return 0.0
        return sum(ratings) / len(ratings)

    async def get_rating_distribution(
        self, product_id: Identity
    ) -> dict[int, int]:
        distribution = {i: 0 for i in range(1, 6)}
        for rating_obj in self._ratings.values():
            if rating_obj.product_id.value == product_id.value:
                distribution[rating_obj.value] += 1
        return distribution


class FakeProductRepository(ProductRepository):
    def __init__(self) -> None:
        self._products: dict[int, Product] = {}

    async def by_identity(self, product_id: Identity) -> Product | None:  # type: ignore[override]
        return self._products.get(product_id.value or -1)

    async def list_by_seller(
        self, seller_id: Identity, limit: int = 20, offset: int = 0
    ) -> list[Product]:  # type: ignore[override]
        return []

    async def list_by_category(
        self, category_id: Identity, limit: int = 20, offset: int = 0
    ) -> list[Product]:  # type: ignore[override]
        return []

    async def list(self, limit: int = 20, offset: int = 0) -> list[Product]:  # type: ignore[override]
        return []

    def add(self, product: Product) -> None:  # type: ignore[override]
        self._products[product.identity.value] = product

    def update(self, product: Product) -> None:  # type: ignore[override]
        self._products[product.identity.value] = product

    async def delete(self, product_id: Identity) -> None:  # type: ignore[override]
        if product_id.value in self._products:
            del self._products[product_id.value]

    async def remove(self, product: Product) -> None:  # type: ignore[override]
        if product.identity.value in self._products:
            del self._products[product.identity.value]


def make_product(product_id: int) -> Product:
    return Product(
        identity=Identity(product_id),
        name="Test Product",
        description="Description",
        price=10.00,
        discount=0,
        stock_quantity=10,
        owner_id=Identity(1),
        category_id=Identity(1),
        is_active=True,
    )


# --- Request Validation Tests ---


def test_create_rating_request_valid() -> None:
    req = CreateRatingRequest(product_id=1, value=5)
    assert req.product_id == 1
    assert req.value == 5


def test_create_rating_request_value_too_low() -> None:
    with pytest.raises(ValidationError):
        CreateRatingRequest(product_id=1, value=0)


def test_create_rating_request_value_too_high() -> None:
    with pytest.raises(ValidationError):
        CreateRatingRequest(product_id=1, value=6)


# --- Factory Tests ---


@pytest.mark.asyncio
async def test_create_rating_success() -> None:
    rating_repo = FakeRatingRepository()
    product_repo = FakeProductRepository()

    # Setup product
    product = make_product(1)
    product_repo.add(product)

    factory = RatingFactory(rating_repo, product_repo)

    req = CreateRatingRequest(product_id=1, value=5)

    rating = await factory.create(req, user_id=100)

    assert rating.product_id.value == 1
    assert rating.user_id.value == 100
    assert rating.value == 5


@pytest.mark.asyncio
async def test_create_rating_product_not_found() -> None:
    rating_repo = FakeRatingRepository()
    product_repo = FakeProductRepository()

    factory = RatingFactory(rating_repo, product_repo)

    req = CreateRatingRequest(product_id=999, value=5)

    with pytest.raises(EntityNotFound):
        await factory.create(req, user_id=100)
