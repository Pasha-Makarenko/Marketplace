from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.seller.repository import SellerRepository
from marketplace.domain.entities.seller.seller import Seller
from marketplace.domain.entities.user.repository import UserRepository
from marketplace.domain.exceptions import DomainError, EntityNotFound


class CreateSellerRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    user_id: int
    store_name: Annotated[
        str, StringConstraints(strip_whitespace=True, max_length=255)
    ]
    contact_info: str | None = None
    return_policy: str | None = None
    delivery_terms: str | None = None


class SellerFactory:
    def __init__(
        self,
        seller_repository: SellerRepository,
        user_repository: UserRepository,
    ) -> None:
        self._seller_repository = seller_repository
        self._user_repository = user_repository

    async def create(self, data: CreateSellerRequest) -> Seller:
        user_identity = Identity(data.user_id)
        user = await self._user_repository.by_identity(user_identity)

        if not user:
            raise EntityNotFound(
                field_name="user",
                value=data.user_id,
            )

        is_user_identity_unique = (
            await self._seller_repository.is_user_identity_unique(
                user_identity
            )
        )

        if not is_user_identity_unique:
            raise DomainError("This user already is seller")

        seller = Seller(
            identity=Identity(_value=None),
            user_id=user_identity,
            store_name=data.store_name,
            store_logs=None,
            contact_info=data.contact_info,
            return_policy=data.return_policy,
            delivery_terms=data.delivery_terms,
            is_active=True,
        )

        return seller
