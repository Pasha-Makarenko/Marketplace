from marketplace.application.common.id_provider import IdProvider
from marketplace.application.common.transaction_manager import (
    TransactionManager,
)
from marketplace.domain.entities.review.factory import (
    CreateReviewRequest,
    ReviewFactory,
)
from marketplace.domain.entities.review.repository import ReviewRepository


class CreateReview:
    def __init__(
        self,
        review_factory: ReviewFactory,
        review_repository: ReviewRepository,
        tr_manager: TransactionManager,
        id_provider: IdProvider,
    ) -> None:
        self._review_factory = review_factory
        self._review_repository = review_repository
        self._tr_manager = tr_manager
        self._id_provider = id_provider

    async def __call__(self, data: CreateReviewRequest) -> int:
        user_id = await self._id_provider.get_current_user_id()
        review = await self._review_factory.create(data=data, user_id=user_id)
        self._review_repository.add(review)
        await self._tr_manager.commit()
        return review.identity.value
