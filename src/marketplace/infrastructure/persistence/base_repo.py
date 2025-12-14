from typing import Generic, Type, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class Repository(Generic[T]):
    model: Type[T]

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def add(self, entity: T) -> None:
        self._session.add(entity)
