from dataclasses import dataclass

from fastapi import HTTPException

from marketplace.domain.entities.user.hasher import PasswordHasher
from marketplace.infrastructure.exceptions import UnauthorizedError
from marketplace.infrastructure.persistence.user_repo import SQLUserRepository


@dataclass
class LoginAuthRequest:
    email: str
    password: str


class Auther:
    def __init__(
        self, hasher: PasswordHasher, user_repo: SQLUserRepository
    ) -> None:
        self._hasher = hasher
        self._user_repo = user_repo

    async def authenticate(self, data: LoginAuthRequest) -> int:
        user = await self._user_repo.by_email(email=data.email)

        if not user:
            raise UnauthorizedError()

        is_valid_password = self._hasher.verify(
            password=data.password, hashed_password=user.hashed_password
        )

        if (data.email != user.email) or not is_valid_password:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        return user.identity.value
