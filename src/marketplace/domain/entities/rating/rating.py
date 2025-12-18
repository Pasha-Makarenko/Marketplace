from dataclasses import dataclass

from marketplace.domain.entities.identity import Identity


@dataclass
class Rating:
    identity: Identity
    user_id: Identity
    product_id: Identity
    value: int
