from datetime import datetime, timezone

import pytest
from freezegun import freeze_time
from pydantic import ValidationError

from marketplace.application.common.transaction_manager import (
    TransactionManager,
)
from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.seller.factory import (
    CreateSellerRequest,
    SellerFactory,
)
from marketplace.domain.entities.seller.repository import SellerRepository
from marketplace.domain.entities.seller.seller import Seller
from marketplace.domain.entities.user.repository import UserRepository
from marketplace.domain.entities.user.user import User
from marketplace.domain.entities.user.value_objects import Phone
from marketplace.domain.exceptions import DomainError, EntityNotFound

# --- Mocks ---


class FakeTransactionManager(TransactionManager):
    async def commit(self) -> None:  # type: ignore[override]
        return None

    async def flush(self) -> None:  # type: ignore[override]
        return None


class FakeUserRepository(UserRepository):
    def __init__(self) -> None:
        self._users: dict[int, User] = {}

    async def by_identity(self, user_id: Identity) -> User | None:  # type: ignore[override]
        return self._users.get(user_id.value or -1)

    async def is_email_unique(self, email: str) -> bool:  # type: ignore[override]
        return True

    def add(self, user: User) -> None:  # type: ignore[override]
        if user.identity.value is not None:
            self._users[user.identity.value] = user


class FakeSellerRepository(SellerRepository):
    def __init__(self) -> None:
        self._sellers: dict[int, Seller] = {}
        self._seq = 1

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
        return not any(
            s.user_id.value == user_id.value for s in self._sellers.values()
        )

    def add(self, seller: Seller) -> None:  # type: ignore[override]
        if seller.identity._value is None:
            new_id = self._seq
            self._seq += 1
            object.__setattr__(seller, "identity", Identity(_value=new_id))
        self._sellers[seller.identity.value] = seller


def make_user(user_id: int) -> User:
    return User(
        identity=Identity(user_id),
        first_name="Test",
        last_name="User",
        email=f"test{user_id}@example.com",
        hashed_password="hash",
        phone=Phone("+1234567890"),
        registered_at=datetime.now(timezone.utc),
    )


def make_seller() -> Seller:
    return Seller(
        identity=Identity(1),
        user_id=Identity(100),
        store_name="Initial Store",
        store_logs=None,
        contact_info="Initial Contact",
        return_policy="Initial Policy",
        delivery_terms="Initial Terms",
        is_active=True,
    )


# --- Entity Tests ---


def test_set_store_name_updates_value() -> None:
    seller = make_seller()
    seller.set_store_name("New Store Name")
    assert seller.store_name == "New Store Name"


def test_set_contact_info_updates_value() -> None:
    seller = make_seller()
    seller.set_contact_info("New Contact Info")
    assert seller.contact_info == "New Contact Info"


def test_set_return_policy_updates_value() -> None:
    seller = make_seller()
    seller.set_return_policy("New Return Policy")
    assert seller.return_policy == "New Return Policy"


def test_set_delivery_terms_updates_value() -> None:
    seller = make_seller()
    seller.set_delivery_terms("New Delivery Terms")
    assert seller.delivery_terms == "New Delivery Terms"


def test_inactivate_sets_is_active_false() -> None:
    seller = make_seller()
    assert seller.is_active is True
    seller.inactivate()
    assert seller.is_active is False


# --- Request Validation Tests ---


def test_create_seller_request_valid() -> None:
    req = CreateSellerRequest(
        user_id=1,
        store_name="Valid Store",
        contact_info="Contact",
        return_policy="Policy",
        delivery_terms="Terms",
    )
    assert req.user_id == 1
    assert req.store_name == "Valid Store"
    assert req.contact_info == "Contact"
    assert req.return_policy == "Policy"
    assert req.delivery_terms == "Terms"


def test_create_seller_request_store_name_stripped() -> None:
    req = CreateSellerRequest(
        user_id=1,
        store_name="  Strip Me  ",
    )
    assert req.store_name == "Strip Me"


def test_create_seller_request_store_name_too_long() -> None:
    long_name = "a" * 256
    with pytest.raises(ValidationError):
        CreateSellerRequest(
            user_id=1,
            store_name=long_name,
        )


def test_create_seller_request_optional_fields_none() -> None:
    req = CreateSellerRequest(
        user_id=1,
        store_name="Store",
    )
    assert req.contact_info is None
    assert req.return_policy is None
    assert req.delivery_terms is None


# --- Factory Tests ---


@freeze_time("2023-01-01 12:00:00")
@pytest.mark.asyncio
async def test_create_seller_success() -> None:
    user_repo = FakeUserRepository()
    seller_repo = FakeSellerRepository()

    # Setup existing user
    user = make_user(1)
    user_repo.add(user)

    factory = SellerFactory(seller_repo, user_repo)
    req = CreateSellerRequest(
        user_id=1,
        store_name="My Store",
        contact_info="Contact",
        return_policy="Policy",
        delivery_terms="Terms",
    )

    seller = await factory.create(req)

    assert seller.user_id.value == 1
    assert seller.store_name == "My Store"


@pytest.mark.asyncio
async def test_create_seller_user_not_found() -> None:
    user_repo = FakeUserRepository()
    seller_repo = FakeSellerRepository()

    factory = SellerFactory(seller_repo, user_repo)
    req = CreateSellerRequest(
        user_id=999,  # User does not exist
        store_name="My Store",
    )

    with pytest.raises(EntityNotFound):
        await factory.create(req)


@freeze_time("2023-01-01 12:00:00")
@pytest.mark.asyncio
async def test_create_seller_already_exists() -> None:
    user_repo = FakeUserRepository()
    seller_repo = FakeSellerRepository()

    # Setup existing user
    user = make_user(1)
    user_repo.add(user)

    factory = SellerFactory(seller_repo, user_repo)
    req = CreateSellerRequest(
        user_id=1,
        store_name="My Store",
    )

    # First creation
    seller = await factory.create(req)
    seller_repo.add(seller)

    # Second creation for same user should fail
    with pytest.raises(DomainError, match="This user already is seller"):
        await factory.create(req)
