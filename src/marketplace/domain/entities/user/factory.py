from datetime import datetime, timezone
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, StringConstraints

from marketplace.application.common.transaction_manager import (
    TransactionManager,
)
from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.user.hasher import PasswordHasher
from marketplace.domain.entities.user.repository import UserRepository
from marketplace.domain.entities.user.user import User
from marketplace.domain.entities.user.value_objects import Phone
from marketplace.domain.exceptions import DomainError


class CreateUserRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    first_name: Annotated[
        str, StringConstraints(strip_whitespace=True, max_length=30)
    ]
    last_name: Annotated[
        str, StringConstraints(strip_whitespace=True, max_length=30)
    ]
    email: EmailStr
    password: Annotated[
        str,
        StringConstraints(
            strip_whitespace=False,
            min_length=8,
            max_length=128,
        ),
    ]
    phone: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
            min_length=8,
            max_length=20,
        ),
    ]


class UserFactory:
    def __init__(
        self,
        user_repository: UserRepository,
        hasher: PasswordHasher,
        transaction_manager: TransactionManager,
    ) -> None:
        self._user_repository = user_repository
        self._hasher = hasher
        self._transaction_manager = transaction_manager

    async def create(self, data: CreateUserRequest) -> User:
        is_email_unique = await self._user_repository.is_email_unique(
            data.email
        )

        if not is_email_unique:
            raise DomainError("Email already exists")

        phone = Phone(data.phone)

        hashed_password = self._hasher.hash(data.password)

        user = User(
            identity=Identity(_value=None),
            first_name=data.first_name,
            last_name=data.last_name,
            email=str(data.email),
            hashed_password=hashed_password,
            phone=phone,
            registered_at=datetime.now(timezone.utc),
        )

        self._user_repository.add(user)

        await self._transaction_manager.flush()

        return user
