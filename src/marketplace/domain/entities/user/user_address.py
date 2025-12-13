from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UserAddress:
    country: str
    city: str
    street: str
    house_number: str
    apartment_number: str | None
    postal_code: str
    is_default: bool
