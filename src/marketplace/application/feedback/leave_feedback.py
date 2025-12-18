from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from marketplace.application.common.id_provider import IdProvider
from marketplace.application.common.transaction_manager import (
    TransactionManager,
)
from marketplace.domain.entities.rating.factory import (
    CreateRatingRequest,
    RatingFactory,
)
from marketplace.domain.entities.rating.repository import RatingRepository
from marketplace.domain.entities.review.factory import (
    CreateReviewRequest,
    ReviewFactory,
)
from marketplace.domain.entities.review.repository import ReviewRepository


class LeaveFeedbackRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    product_id: int
    rating: Annotated[int, Field(ge=1, le=5)]
    comment: Annotated[
        str | None, StringConstraints(strip_whitespace=True, max_length=1000)
    ] = None


class LeaveFeedback:
    def __init__(
        self,
        rating_factory: RatingFactory,
        review_factory: ReviewFactory,
        rating_repository: RatingRepository,
        review_repository: ReviewRepository,
        transaction_manager: TransactionManager,
        id_provider: IdProvider,
    ) -> None:
        self._rating_factory = rating_factory
        self._review_factory = review_factory
        self._rating_repository = rating_repository
        self._review_repository = review_repository
        self._transaction_manager = transaction_manager
        self._id_provider = id_provider

    async def __call__(self, data: LeaveFeedbackRequest) -> None:
        user_id = await self._id_provider.get_current_user_id()

        rating = await self._rating_factory.create(
            CreateRatingRequest(
                product_id=data.product_id,
                value=data.rating,
            ),
            user_id=user_id,
        )
        self._rating_repository.add(rating)

        review = await self._review_factory.create(
            CreateReviewRequest(
                product_id=data.product_id,
                text=data.comment,
            ),
            user_id=user_id,
        )
        self._review_repository.add(review)

        await self._transaction_manager.commit()
