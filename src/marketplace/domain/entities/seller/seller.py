from dataclasses import dataclass

from marketplace.domain.entities.identity import Identity


@dataclass
class Seller:
    identity: Identity
    user_id: Identity
    store_name: str
    contact_info: str
    return_policy: str
    delivery_terms: str