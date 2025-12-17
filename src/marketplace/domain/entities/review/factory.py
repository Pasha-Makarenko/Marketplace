from datetime import datetime, timezone
from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.product.repository import ProductRepository
from marketplace.domain.entities.review.repository import ReviewRepository
from marketplace.domain.entities.review.review import Review
from marketplace.domain.exceptions import EntityNotFound


class CreateReviewRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    product_id: int
    text: Annotated[
        str | None, StringConstraints(strip_whitespace=True, max_length=1000)
    ] = None


class ReviewFactory:
    def __init__(
        self,
        review_repository: ReviewRepository,
        product_repository: ProductRepository,
    ) -> None:
        self._review_repository = review_repository
        self._product_repository = product_repository

    async def create(self, data: CreateReviewRequest, user_id: int) -> Review:
        product_identity = Identity(data.product_id)

        product = await self._product_repository.by_identity(product_identity)
        if not product:
            raise EntityNotFound(
                field_name="product_id", value=data.product_id
            )

        review = Review(
            identity=Identity(_value=None),
            author_id=Identity(user_id),
            product_id=product_identity,
            text=data.text,
            created_at=datetime.now(timezone.utc),
        )

        return review
