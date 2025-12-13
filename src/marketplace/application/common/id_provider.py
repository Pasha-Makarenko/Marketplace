from abc import abstractmethod
from typing import Protocol


class IdProvider(Protocol):
    @abstractmethod
    async def get_current_user_id(self) -> int: ...

    @abstractmethod
    async def get_user(self) -> User: ...