from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.product.repository import ProductRepository
from marketplace.domain.entities.rating.rating import Rating
from marketplace.domain.entities.rating.repository import RatingRepository
from marketplace.domain.exceptions import EntityNotFound


class CreateRatingRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    product_id: int
    value: Annotated[int, Field(ge=1, le=5)]


class RatingFactory:
    def __init__(
        self,
        rating_repository: RatingRepository,
        product_repository: ProductRepository,
    ) -> None:
        self._rating_repository = rating_repository
        self._product_repository = product_repository

    async def create(self, data: CreateRatingRequest, user_id: int) -> Rating:
        product_identity = Identity(data.product_id)

        product = await self._product_repository.by_identity(product_identity)
        if not product:
            raise EntityNotFound(
                field_name="product_id", value=data.product_id
            )

        rating = Rating(
            identity=Identity(_value=None),
            user_id=Identity(user_id),
            product_id=product_identity,
            value=data.value,
        )

        return rating
