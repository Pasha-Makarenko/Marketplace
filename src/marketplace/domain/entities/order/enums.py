from enum import StrEnum, auto


class OrderStatus(StrEnum):
    DRAFT = auto()
    PENDING_PAYMENT = auto()
    PAID = auto()
    FULFILLED = auto()
    CANCELLED = auto()


class PaymentStatus(StrEnum):
    PENDING = auto()
    PAID = auto()
    FAILED = auto()
    REFUNDED = auto()


class DeliveryStatus(StrEnum):
    PENDING = auto()
    SHIPPED = auto()
    DELIVERED = auto()
    CANCELLED = auto()
