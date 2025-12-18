from dataclasses import dataclass
from datetime import datetime

from marketplace.domain.entities.identity import Identity


@dataclass
class Review:
    identity: Identity
    author_id: Identity
    product_id: Identity
    text: str | None
    created_at: datetime
