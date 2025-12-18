from abc import abstractmethod
from typing import Protocol

from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.review.review import Review


class ReviewRepository(Protocol):
    @abstractmethod
    def add(self, review: Review) -> None:
        raise NotImplementedError

    @abstractmethod
    async def by_identity(self, review_id: Identity) -> Review | None:
        raise NotImplementedError

    @abstractmethod
    async def list_by_product(
        self, product_id: Identity, limit: int, offset: int
    ) -> list[Review]:
        raise NotImplementedError

    @abstractmethod
    async def get_recent_reviews(self, limit: int) -> list[Review]:
        raise NotImplementedError
