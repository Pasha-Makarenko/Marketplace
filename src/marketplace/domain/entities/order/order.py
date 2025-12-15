from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal
from typing import List

from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.order.enums import (
    DeliveryStatus,
    OrderStatus,
    PaymentStatus,
)
from marketplace.domain.entities.order.order_item import OrderItem
from marketplace.domain.exceptions import DomainError

__all__ = ["Order", "OrderItem", "Payment", "Delivery"]


def _money(value: Decimal | int | float) -> Decimal:
    return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@dataclass
class Payment:
    status: PaymentStatus = PaymentStatus.PENDING
    transaction_id: str | None = None
    paid_at: datetime | None = None

    def __composite_values__(
        self,
    ) -> tuple[PaymentStatus, str | None, datetime | None]:
        return (self.status, self.transaction_id, self.paid_at)

    def mark_paid(self, transaction_id: str) -> None:
        self.status = PaymentStatus.PAID
        self.transaction_id = transaction_id
        self.paid_at = datetime.now(timezone.utc)


@dataclass
class Delivery:
    status: DeliveryStatus = DeliveryStatus.PENDING
    tracking_number: str | None = None
    address: str | None = None
    delivered_at: datetime | None = None

    def __composite_values__(
        self,
    ) -> tuple[DeliveryStatus, str | None, str | None, datetime | None]:
        return (
            self.status,
            self.tracking_number,
            self.address,
            self.delivered_at,
        )

    def mark_shipped(self, tracking_number: str) -> None:
        self.status = DeliveryStatus.SHIPPED
        self.tracking_number = tracking_number

    def mark_delivered(self) -> None:
        self.status = DeliveryStatus.DELIVERED
        self.delivered_at = datetime.now(timezone.utc)


@dataclass
class Order:
    identity: Identity
    user_identity: Identity
    items: List[OrderItem] = field(default_factory=list)
    status: OrderStatus = OrderStatus.DRAFT
    payment: Payment = field(default_factory=Payment)
    delivery: Delivery = field(default_factory=Delivery)
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def add_item(self, item: OrderItem) -> None:
        if self.status in (OrderStatus.PAID, OrderStatus.FULFILLED):
            raise DomainError("Cannot modify a paid or fulfilled order")
        existing = next(
            (i for i in self.items if i.product_id == item.product_id),
            None,
        )
        if existing:
            # merge quantities
            new_qty = existing.quantity + item.quantity
            self.items.remove(existing)
            merged = OrderItem(
                product_id=item.product_id,
                quantity=new_qty,
                price_at_purchase=item.price_at_purchase,
                title=item.title,
            )
            self.items.append(merged)
        else:
            self.items.append(item)
        self.updated_at = datetime.now(timezone.utc)

    def remove_item(self, product_id: int) -> None:
        if self.status in (OrderStatus.PAID, OrderStatus.FULFILLED):
            raise DomainError("Cannot modify a paid or fulfilled order")
        self.items = [i for i in self.items if i.product_id != product_id]
        self.updated_at = datetime.now(timezone.utc)

    @property
    def total_amount(self) -> Decimal:
        return _money(sum(item.line_total for item in self.items))

    def submit(self) -> None:
        if not self.items:
            raise DomainError("Order must have at least one item")
        self.status = OrderStatus.PENDING_PAYMENT
        self.updated_at = datetime.now(timezone.utc)

    def mark_paid(self, transaction_id: str) -> None:
        if self.status not in (
            OrderStatus.PENDING_PAYMENT,
            OrderStatus.DRAFT,
        ):
            raise DomainError("Order is not payable in current status")
        self.payment.mark_paid(transaction_id)
        self.status = OrderStatus.PAID
        self.updated_at = datetime.now(timezone.utc)

    def mark_fulfilled(self) -> None:
        if self.status != OrderStatus.PAID:
            raise DomainError("Only paid orders can be fulfilled")
        self.delivery.mark_shipped(self.delivery.tracking_number or "")
        self.status = OrderStatus.FULFILLED
        self.updated_at = datetime.now(timezone.utc)

    def cancel(self) -> None:
        if self.status in (OrderStatus.PAID, OrderStatus.FULFILLED):
            raise DomainError("Cannot cancel paid or fulfilled order")
        self.status = OrderStatus.CANCELLED
        self.updated_at = datetime.now(timezone.utc)
