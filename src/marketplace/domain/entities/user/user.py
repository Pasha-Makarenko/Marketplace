from dataclasses import dataclass
from datetime import datetime

from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.user.value_objects import Phone


@dataclass
class User:
    identity: Identity
    first_name: str
    last_name: str
    email: str
    hashed_password: str
    phone: Phone
    registered_at: datetime

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
