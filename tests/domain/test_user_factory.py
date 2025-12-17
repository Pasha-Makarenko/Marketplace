import pytest

from marketplace.application.common.transaction_manager import (
    TransactionManager,
)
from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.user.factory import (
    CreateUserRequest,
    UserFactory,
)
from marketplace.domain.entities.user.hasher import PasswordHasher
from marketplace.domain.entities.user.repository import UserRepository
from marketplace.domain.entities.user.user import User
from marketplace.domain.exceptions import DomainError


class FakeHasher(PasswordHasher):
    def hash(self, password: str) -> str:  # type: ignore[override]
        return f"hashed:{password}"

    def verify(self, password: str, hashed_password: str) -> bool:  # type: ignore[override]
        return hashed_password == f"hashed:{password}"


class FakeTransactionManager(TransactionManager):
    async def commit(self) -> None:  # type: ignore[override]
        return None

    async def flush(self) -> None:  # type: ignore[override]
        return None


class FakeUserRepository(UserRepository):
    def __init__(self) -> None:
        self._by_email: dict[str, User] = {}
        self._by_id: dict[int, User] = {}
        self._seq = 1

    async def by_identity(self, user_id: Identity) -> User | None:  # type: ignore[override]
        return self._by_id.get(user_id.value or -1)

    async def is_email_unique(self, email: str) -> bool:  # type: ignore[override]
        return email not in self._by_email

    def add(self, user: User) -> None:  # type: ignore[override]
        if user.identity._value is None:
            new_id = self._seq
            self._seq += 1
            object.__setattr__(user, "identity", Identity(_value=new_id))
        self._by_id[user.identity.value] = user
        self._by_email[user.email] = user


@pytest.mark.asyncio
async def test_create_user_success() -> None:
    repo = FakeUserRepository()
    factory = UserFactory(repo, FakeHasher())
    req = CreateUserRequest(
        first_name="John",
        last_name="Doe",
        email="user@example.com",
        password="supersecret",
        phone="+380501112233",
    )

    user = await factory.create(req)

    assert user.email == "user@example.com"
    assert user.hashed_password == "hashed:supersecret"


@pytest.mark.asyncio
async def test_duplicate_email_raises_domain_error() -> None:
    repo = FakeUserRepository()
    factory = UserFactory(repo, FakeHasher())
    req = CreateUserRequest(
        first_name="John",
        last_name="Doe",
        email="user@example.com",
        password="supersecret",
        phone="+380501112233",
    )

    user = await factory.create(req)
    repo.add(user)

    with pytest.raises(DomainError):
        await factory.create(req)
