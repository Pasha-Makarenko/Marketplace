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
    is_active: bool

    def set_store_name(self, store_name: str) -> None:
        self.store_name = store_name

    def set_contact_info(self, contact_info: str) -> None:
        self.contact_info = contact_info

    def set_return_policy(self, return_policy: str) -> None:
        self.return_policy = return_policy

    def set_delivery_terms(self, delivery_terms: str) -> None:
        self.delivery_terms = delivery_terms

    def inactivate(self) -> None:
        self.is_active = False
