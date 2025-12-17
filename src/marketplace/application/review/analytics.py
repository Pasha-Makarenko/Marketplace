from dataclasses import dataclass

from marketplace.domain.entities.review.repository import ReviewRepository
from marketplace.domain.entities.review.review import Review


@dataclass(frozen=True, slots=True)
class GetRecentReviewsRequest:
    limit: int = 10


class GetRecentReviews:
    def __init__(self, review_repository: ReviewRepository) -> None:
        self._review_repository = review_repository

    async def __call__(self, data: GetRecentReviewsRequest) -> list[Review]:
        return await self._review_repository.get_recent_reviews(
            limit=data.limit
        )
