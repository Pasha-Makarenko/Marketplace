from dataclasses import dataclass

from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.rating.repository import RatingRepository


@dataclass(frozen=True, slots=True)
class GetRatingDistributionRequest:
    product_id: int


class GetRatingDistribution:
    def __init__(self, rating_repository: RatingRepository) -> None:
        self._rating_repository = rating_repository

    async def __call__(
        self, data: GetRatingDistributionRequest
    ) -> dict[int, int]:
        return await self._rating_repository.get_rating_distribution(
            product_id=Identity(data.product_id)
        )


@dataclass(frozen=True, slots=True)
class GetProductAverageRatingRequest:
    product_id: int


class GetProductAverageRating:
    def __init__(self, rating_repository: RatingRepository) -> None:
        self._rating_repository = rating_repository

    async def __call__(self, data: GetProductAverageRatingRequest) -> float:
        return await self._rating_repository.get_average_for_product(
            product_id=Identity(data.product_id)
        )
