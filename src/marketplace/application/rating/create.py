from marketplace.application.common.id_provider import IdProvider
from marketplace.application.common.transaction_manager import (
    TransactionManager,
)
from marketplace.domain.entities.rating.factory import (
    CreateRatingRequest,
    RatingFactory,
)
from marketplace.domain.entities.rating.repository import RatingRepository


class CreateRating:
    def __init__(
        self,
        rating_factory: RatingFactory,
        rating_repository: RatingRepository,
        tr_manager: TransactionManager,
        id_provider: IdProvider,
    ) -> None:
        self._rating_factory = rating_factory
        self._rating_repository = rating_repository
        self._tr_manager = tr_manager
        self._id_provider = id_provider

    async def __call__(self, data: CreateRatingRequest) -> int:
        user_id = await self._id_provider.get_current_user_id()
        rating = await self._rating_factory.create(data=data, user_id=user_id)
        self._rating_repository.add(rating)
        await self._tr_manager.commit()
        return rating.identity.value
