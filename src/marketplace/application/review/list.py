from dataclasses import dataclass

from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.review.repository import ReviewRepository
from marketplace.domain.entities.review.review import Review


@dataclass(frozen=True, slots=True)
class ListReviewsRequest:
    product_id: int
    limit: int = 20
    offset: int = 0


class ListReviews:
    def __init__(self, review_repository: ReviewRepository) -> None:
        self._review_repository = review_repository

    async def __call__(self, data: ListReviewsRequest) -> list[Review]:
        return await self._review_repository.list_by_product(
            product_id=Identity(data.product_id),
            limit=data.limit,
            offset=data.offset,
        )
