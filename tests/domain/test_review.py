from datetime import datetime, timezone
from decimal import Decimal

import pytest
from freezegun import freeze_time
from pydantic import ValidationError

from marketplace.application.common.id_provider import IdProvider
from marketplace.application.common.transaction_manager import (
    TransactionManager,
)
from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.product.product import Product
from marketplace.domain.entities.product.repository import ProductRepository
from marketplace.domain.entities.review.factory import (
    CreateReviewRequest,
    ReviewFactory,
)
from marketplace.domain.entities.review.repository import ReviewRepository
from marketplace.domain.entities.review.review import Review
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


class FakeProductRepository(ProductRepository):
    def __init__(self) -> None:
        self._products: dict[int, Product] = {}

    async def by_identity(self, product_id: Identity) -> Product | None:  # type: ignore[override]
        return self._products.get(product_id.value or -1)

    # Dummy implementations for other methods to satisfy Protocol instantiation
    async def list_by_seller(self, seller_id: Identity) -> list[Product]:  # type: ignore[override]
        return []

    async def list_by_category(self, category_id: Identity) -> list[Product]:  # type: ignore[override]
        return []

    async def list(self, **kwargs) -> list[Product]:  # type: ignore[override]
        return []

    def add(self, product: Product) -> None:  # type: ignore[override]
        self._products[product.identity.value] = product

    async def remove(self, product: Product) -> None:  # type: ignore[override]
        pass


class FakeReviewRepository(ReviewRepository):
    def __init__(self) -> None:
        self._reviews: dict[int, Review] = {}
        self._seq = 1

    def add(self, review: Review) -> None:  # type: ignore[override]
        if review.identity._value is None:
            new_id = self._seq
            self._seq += 1
            object.__setattr__(review, "identity", Identity(_value=new_id))
        self._reviews[review.identity.value] = review

    async def by_identity(self, review_id: Identity) -> Review | None:  # type: ignore[override]
        return self._reviews.get(review_id.value or -1)

    async def list_by_product(  # type: ignore[override]
        self, product_id: Identity, limit: int, offset: int
    ) -> list[Review]:
        return [
            r
            for r in self._reviews.values()
            if r.product_id.value == product_id.value
        ]

    async def get_recent_reviews(self, limit: int) -> list[Review]:  # type: ignore[override]
        # Sort by created_at in descending order and return up to 'limit'
        # reviews
        sorted_reviews = sorted(
            self._reviews.values(), key=lambda r: r.created_at, reverse=True
        )
        return sorted_reviews[:limit]


def make_product(product_id: int) -> Product:
    return Product(
        identity=Identity(product_id),
        name="Test Product",
        description="Desc",
        price=Decimal("10.00"),
        discount=0,
        stock_quantity=10,
        owner_id=Identity(1),
        category_id=Identity(1),
        is_active=True,
    )


# --- Request Validation Tests ---


def test_create_review_request_valid() -> None:
    req = CreateReviewRequest(product_id=1, text="Good")
    assert req.product_id == 1
    assert req.text == "Good"


def test_create_review_request_text_too_long() -> None:
    long_text = "a" * 1001
    with pytest.raises(ValidationError):
        CreateReviewRequest(product_id=1, text=long_text)


def test_create_review_request_text_stripped() -> None:
    req = CreateReviewRequest(product_id=1, text="  Good  ")
    assert req.text == "Good"


# --- Factory Tests ---


@freeze_time("2023-01-01 12:00:00")
@pytest.mark.asyncio
async def test_create_review_success() -> None:
    review_repo = FakeReviewRepository()
    product_repo = FakeProductRepository()

    # Setup existing product
    product = make_product(1)
    product_repo.add(product)

    factory = ReviewFactory(review_repo, product_repo)

    req = CreateReviewRequest(
        product_id=1,
        text="Great product!",
    )

    review = await factory.create(req, user_id=100)

    assert review.product_id.value == 1
    assert review.author_id.value == 100
    assert review.text == "Great product!"
    assert review.created_at == datetime(
        2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc
    )


@pytest.mark.asyncio
async def test_create_review_product_not_found() -> None:
    review_repo = FakeReviewRepository()
    product_repo = FakeProductRepository()

    factory = ReviewFactory(review_repo, product_repo)

    req = CreateReviewRequest(
        product_id=999,  # Product does not exist
        text="Great product!",
    )

    with pytest.raises(EntityNotFound):
        await factory.create(req, user_id=100)
