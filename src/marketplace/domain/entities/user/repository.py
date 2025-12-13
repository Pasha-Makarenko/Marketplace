from abc import abstractmethod
from typing import Protocol

from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.user.user import User


class UserRepository(Protocol):
    @abstractmethod
    async def by_identity(self, user_id: Identity) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def is_email_unique(self, email: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def add(self, user: User) -> None:
        raise NotImplementedError
