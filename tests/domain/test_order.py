from datetime import datetime, timezone
from decimal import Decimal

import pytest

from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.order.enums import (
    DeliveryStatus,
    OrderStatus,
    PaymentStatus,
)
from marketplace.domain.entities.order.order import Order
from marketplace.domain.entities.order.order_item import OrderItem
from marketplace.domain.exceptions import DomainError


def make_order(user_id: int = 1) -> Order:
    return Order(
        identity=Identity(_value=None), user_identity=Identity(_value=user_id)
    )


def test_add_item_merges_same_product_and_updates_total() -> None:
    order = make_order()
    order.add_item(
        OrderItem(
            product_id=10,
            quantity=1,
            price_at_purchase=Decimal("5.00"),
            title="A",
        )
    )
    order.add_item(
        OrderItem(
            product_id=10,
            quantity=2,
            price_at_purchase=Decimal("5.00"),
            title="A",
        )
    )

    assert len(order.items) == 1
    item = order.items[0]
    assert item.quantity == 3
    assert order.total_amount == Decimal("15.00")


def test_submit_requires_items() -> None:
    order = make_order()
    with pytest.raises(DomainError):
        order.submit()


def test_submit_sets_status_pending_payment() -> None:
    order = make_order()
    order.add_item(
        OrderItem(
            product_id=1,
            quantity=1,
            price_at_purchase=Decimal("2.50"),
            title="X",
        )
    )

    order.submit()

    assert order.status == OrderStatus.PENDING_PAYMENT


def test_mark_paid_sets_payment_info_and_status() -> None:
    order = make_order()
    order.add_item(
        OrderItem(
            product_id=1,
            quantity=1,
            price_at_purchase=Decimal("2.50"),
            title="X",
        )
    )
    order.submit()

    before = datetime.now(timezone.utc)
    order.mark_paid("txn-123")
    after = datetime.now(timezone.utc)

    assert order.status == OrderStatus.PAID
    assert order.payment.status == PaymentStatus.PAID
    assert order.payment.transaction_id == "txn-123"
    assert order.payment.paid_at is not None
    assert before <= order.payment.paid_at <= after


def test_mark_fulfilled_only_when_paid() -> None:
    order = make_order()
    order.add_item(
        OrderItem(
            product_id=1,
            quantity=1,
            price_at_purchase=Decimal("2.50"),
            title="X",
        )
    )
    order.submit()

    with pytest.raises(DomainError):
        order.mark_fulfilled()

    order.mark_paid("txn-123")
    order.mark_fulfilled()

    assert order.status == OrderStatus.FULFILLED
    assert order.delivery.status == DeliveryStatus.SHIPPED


def test_add_item_after_paid_disallowed() -> None:
    order = make_order()
    order.add_item(
        OrderItem(
            product_id=1,
            quantity=1,
            price_at_purchase=Decimal("2.50"),
            title="X",
        )
    )
    order.submit()
    order.mark_paid("txn-123")

    with pytest.raises(DomainError):
        order.add_item(
            OrderItem(
                product_id=2,
                quantity=1,
                price_at_purchase=Decimal("1.00"),
                title="Y",
            )
        )


def test_cancel_after_paid_forbidden() -> None:
    order = make_order()
    order.add_item(
        OrderItem(
            product_id=1,
            quantity=1,
            price_at_purchase=Decimal("2.50"),
            title="X",
        )
    )
    order.submit()
    order.mark_paid("txn-123")

    with pytest.raises(DomainError):
        order.cancel()
