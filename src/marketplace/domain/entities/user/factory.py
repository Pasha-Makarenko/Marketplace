from datetime import datetime, timezone
from dataclasses import dataclass

from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.user.hasher import PasswordHasher
from marketplace.domain.entities.user.repository import UserRepository
from marketplace.domain.entities.user.user import User
from marketplace.domain.exceptions import DomainError


@dataclass(frozen=True, slots=True)
class CreateUserRequest:
    first_name: str
    last_name: str
    email: str
    password: str
    phone: str

class UserFactory:
    def __init__(
        self, user_repository: UserRepository, hasher: PasswordHasher
    ) -> None:
        self._user_repository = user_repository
        self._hasher = hasher

    async def create(
        self, data: CreateUserRequest
    ) -> User:
        is_email_unique = (
            await self._user_repository.is_email_unique(data.email)
        )

        if not is_email_unique:
            raise DomainError("Email already exists")

        hashed_password = self._hasher.hash(data.password)

        return User(
            identity=Identity(_value=None),
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            hashed_password=hashed_password,
            phone=data.phone,
            registered_at=datetime.now(timezone.utc),
        )