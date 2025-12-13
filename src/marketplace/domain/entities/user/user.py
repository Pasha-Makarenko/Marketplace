from dataclasses import dataclass
from datetime import datetime

from marketplace.domain.entities.identity import Identity


@dataclass
class User:
    identity: Identity
    first_name: str
    last_name: str
    email: str
    hashed_password: str
    phone: str
    registered_at: datetime

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
