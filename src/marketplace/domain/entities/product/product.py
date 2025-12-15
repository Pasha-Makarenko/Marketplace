from dataclasses import dataclass
from decimal import Decimal

from marketplace.domain.entities.identity import Identity
from marketplace.domain.exceptions import DomainError


@dataclass
class Product:
    identity: Identity
    name: str
    description: str | None
    price: Decimal
    discount: int
    stock_quantity: int
    owner_id: Identity
    category_id: Identity

    def change_name(self, name: str) -> None:
        if not name:
            raise DomainError("Product name cannot be empty.")
        self.name = name

    def change_description(self, description: str | None) -> None:
        self.description = description

    def change_price(self, price: Decimal) -> None:
        if price < 0:
            raise DomainError("Price cannot be negative.")
        self.price = price

    def change_discount(self, discount: int) -> None:
        if not (0 <= discount <= 100):
            raise DomainError("Discount must be between 0 and 100.")
        self.discount = discount

    def change_stock_quantity(self, quantity: int) -> None:
        if quantity < 0:
            raise DomainError("Stock quantity cannot be negative.")
        self.stock_quantity = quantity

    def change_category(self, category_id: Identity) -> None:
        self.category_id = category_id
