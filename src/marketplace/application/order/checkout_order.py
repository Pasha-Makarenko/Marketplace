from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable

from marketplace.application.common.id_provider import IdProvider
from marketplace.application.common.transaction_manager import (
    TransactionManager,
)
from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.order.order import Order
from marketplace.domain.entities.order.order_item import OrderItem
from marketplace.domain.entities.order.repository import OrderRepository
from marketplace.domain.exceptions import DomainError


@dataclass(frozen=True, slots=True)
class CheckoutOrderItem:
    product_id: int
    quantity: int
    price_at_purchase: Decimal
    title: str


@dataclass(frozen=True, slots=True)
class CheckoutOrderRequest:
    items: Iterable[CheckoutOrderItem]


class CheckoutOrderCommand:
    def __init__(
        self,
        order_repo: OrderRepository,
        transaction_manager: TransactionManager,
        id_provider: IdProvider,
    ) -> None:
        self._order_repo = order_repo
        self._tm = transaction_manager
        self._id_provider = id_provider

    async def execute(self, data: CheckoutOrderRequest) -> int:
        items = list(data.items)
        if not items:
            raise DomainError("Order must contain at least one item")

        user_id = await self._id_provider.get_current_user_id()
        order = Order(
            identity=Identity(_value=None),
            user_identity=Identity(_value=user_id),
        )

        for item in items:
            order.add_item(
                OrderItem(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price_at_purchase=item.price_at_purchase,
                    title=item.title,
                )
            )

        order.submit()

        self._order_repo.add(order)
        await self._tm.commit()
        return order.identity.value
