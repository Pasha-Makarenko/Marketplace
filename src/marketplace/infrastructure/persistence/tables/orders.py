from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Table,
    text,
)
from sqlalchemy.orm import composite, relationship

from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.order.enums import (
    DeliveryStatus,
    OrderStatus,
    PaymentStatus,
)
from marketplace.domain.entities.order.order import Delivery, Order, Payment
from marketplace.domain.entities.order.order_item import OrderItem
from marketplace.infrastructure.persistence.tables.base import mapper_registry

orders_table = Table(
    "orders",
    mapper_registry.metadata,
    Column("order_id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.user_id"), nullable=False),
    Column(
        "status",
        Enum(OrderStatus, native_enum=False),
        nullable=False,
        server_default=OrderStatus.DRAFT.value,
    ),
    Column(
        "payment_status",
        Enum(PaymentStatus, native_enum=False),
        nullable=False,
        server_default=PaymentStatus.PENDING.value,
    ),
    Column("transaction_id", String(64), nullable=True),
    Column("paid_at", DateTime(timezone=True), nullable=True),
    Column(
        "delivery_status",
        Enum(DeliveryStatus, native_enum=False),
        nullable=False,
        server_default=DeliveryStatus.PENDING.value,
    ),
    Column("tracking_number", String(128), nullable=True),
    Column("delivery_address", String(512), nullable=True),
    Column("delivered_at", DateTime(timezone=True), nullable=True),
    Column(
        "created_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    ),
    Column(
        "updated_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
    ),
)

order_items_table = Table(
    "order_items",
    mapper_registry.metadata,
    Column(
        "order_id",
        Integer,
        ForeignKey("orders.order_id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column("product_id", Integer, primary_key=True),
    Column("title", String(255), nullable=False),
    Column("quantity", Integer, nullable=False),
    Column("price_at_purchase", Numeric(10, 2), nullable=False),
)

mapper_registry.map_imperatively(
    OrderItem,
    order_items_table,
    properties={
        "order_id": order_items_table.c.order_id,
    },
)

mapper_registry.map_imperatively(
    Order,
    orders_table,
    properties={
        "identity": composite(Identity, orders_table.c.order_id),
        "user_identity": composite(Identity, orders_table.c.user_id),
        "payment": composite(
            Payment,
            orders_table.c.payment_status,
            orders_table.c.transaction_id,
            orders_table.c.paid_at,
        ),
        "delivery": composite(
            Delivery,
            orders_table.c.delivery_status,
            orders_table.c.tracking_number,
            orders_table.c.delivery_address,
            orders_table.c.delivered_at,
        ),
        "items": relationship(
            OrderItem,
            cascade="all, delete-orphan",
            collection_class=list,
            primaryjoin=orders_table.c.order_id
            == order_items_table.c.order_id,
        ),
    },
)
