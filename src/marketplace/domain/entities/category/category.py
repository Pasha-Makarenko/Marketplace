from dataclasses import dataclass

from marketplace.domain.entities.identity import Identity
from marketplace.domain.exceptions import DomainError


@dataclass
class Category:
    identity: Identity
    name: str
    parent_category_id: Identity | None

    def rename(self, name: str) -> None:
        if not name:
            raise DomainError("Category name cannot be empty.")
        self.name = name

    def set_parent(self, parent_category_id: Identity | None) -> None:
        if (
            parent_category_id
            and self.identity.value
            and parent_category_id.value == self.identity.value
        ):
            raise DomainError("Category cannot be its own parent.")
        self.parent_category_id = parent_category_id
