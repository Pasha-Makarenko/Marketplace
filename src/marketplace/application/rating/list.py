from dataclasses import dataclass

from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.rating.rating import Rating
from marketplace.domain.entities.rating.repository import RatingRepository


@dataclass(frozen=True, slots=True)
class ListRatingsRequest:
    product_id: int
    limit: int = 20
    offset: int = 0


class ListRatings:
    def __init__(self, rating_repository: RatingRepository) -> None:
        self._rating_repository = rating_repository

    async def __call__(self, data: ListRatingsRequest) -> list[Rating]:
        return await self._rating_repository.list_by_product(
            product_id=Identity(data.product_id),
            limit=data.limit,
            offset=data.offset,
        )
