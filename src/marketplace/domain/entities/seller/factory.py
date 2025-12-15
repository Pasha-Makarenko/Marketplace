from dataclasses import dataclass

from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.seller.repository import SellerRepository
from marketplace.domain.entities.seller.seller import Seller
from marketplace.domain.entities.user.repository import UserRepository
from marketplace.domain.exceptions import DomainError, EntityNotFound


@dataclass(frozen=True, slots=True)
class CreateSellerRequest:
    user_id: Identity
    store_name: str
    contact_info: str
    return_policy: str
    delivery_terms: str


class SellerFactory:
    def __init__(
        self,
        seller_repository: SellerRepository,
        user_repository: UserRepository,
    ) -> None:
        self._seller_repository = seller_repository
        self._user_repository = user_repository

    async def create(self, data: CreateSellerRequest) -> Seller:
        user = self._user_repository.by_identity(data.user_id)

        if not user:
            raise EntityNotFound(
                field_name="user",
                value=data.user_id.value,
            )

        is_user_identity_unique = (
            self._seller_repository.is_user_identity_unique(data.user_id)
        )

        if not is_user_identity_unique:
            raise DomainError("This user already is seller")

        return Seller(
            identity=Identity(_value=None),
            user_id=data.user_id,
            store_name=data.store_name,
            contact_info=data.contact_info,
            return_policy=data.return_policy,
            delivery_terms=data.delivery_terms,
            is_active=True,
        )
