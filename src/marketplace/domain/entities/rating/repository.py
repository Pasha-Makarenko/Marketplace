from abc import abstractmethod
from typing import Protocol

from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.rating.rating import Rating


class RatingRepository(Protocol):
    @abstractmethod
    def add(self, rating: Rating) -> None:
        raise NotImplementedError

    @abstractmethod
    async def by_identity(self, rating_id: Identity) -> Rating | None:
        raise NotImplementedError

    @abstractmethod
    async def list_by_product(
        self, product_id: Identity, limit: int, offset: int
    ) -> list[Rating]:
        raise NotImplementedError

    @abstractmethod
    async def get_average_for_product(self, product_id: Identity) -> float:
        raise NotImplementedError

    @abstractmethod
    async def get_rating_distribution(
        self, product_id: Identity
    ) -> dict[int, int]:
        raise NotImplementedError
