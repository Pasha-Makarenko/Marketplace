from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from marketplace.domain.exceptions import DomainError


def _money(value: Decimal | int | float) -> Decimal:
    return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@dataclass
class OrderItem:
    order_id: int | None = None
    product_id: int | None = None
    quantity: int = 0
    price_at_purchase: Decimal = Decimal("0")
    title: str = ""

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise DomainError("Quantity must be greater than zero")
        if self.price_at_purchase <= 0:
            raise DomainError("Price must be greater than zero")
        self.price_at_purchase = _money(self.price_at_purchase)

    @property
    def line_total(self) -> Decimal:
        return _money(self.price_at_purchase * self.quantity)
