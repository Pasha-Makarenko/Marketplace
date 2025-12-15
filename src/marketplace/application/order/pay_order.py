from dataclasses import dataclass

from marketplace.application.common.id_provider import IdProvider
from marketplace.application.common.transaction_manager import (
    TransactionManager,
)
from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.order.repository import OrderRepository
from marketplace.domain.exceptions import DomainError, EntityNotFound


@dataclass(frozen=True, slots=True)
class PayOrderRequest:
    order_id: int
    transaction_id: str


class PayOrderCommand:
    def __init__(
        self,
        order_repo: OrderRepository,
        transaction_manager: TransactionManager,
        id_provider: IdProvider,
    ) -> None:
        self._order_repo = order_repo
        self._tm = transaction_manager
        self._id_provider = id_provider

    async def execute(self, data: PayOrderRequest) -> None:
        current_user_id = await self._id_provider.get_current_user_id()
        order = await self._order_repo.by_identity(
            Identity(_value=data.order_id)
        )
        if not order:
            raise EntityNotFound("order_id", data.order_id)
        if order.user_identity.value != current_user_id:
            raise DomainError("Cannot pay another user's order")
        order.mark_paid(data.transaction_id)
        await self._tm.commit()
