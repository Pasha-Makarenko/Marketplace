from abc import abstractmethod
from typing import Protocol

from marketplace.domain.entities.category.category import Category
from marketplace.domain.entities.identity import Identity


class CategoryRepository(Protocol):
    @abstractmethod
    async def by_identity(self, category_id: Identity) -> Category | None:
        raise NotImplementedError

    @abstractmethod
    def add(self, category: Category) -> None:
        raise NotImplementedError

    @abstractmethod
    async def remove(self, category: Category) -> None:
        raise NotImplementedError
