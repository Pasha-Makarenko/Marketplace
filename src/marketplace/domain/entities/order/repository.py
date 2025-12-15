from abc import abstractmethod
from typing import Protocol

from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.order.order import Order


class OrderRepository(Protocol):
    @abstractmethod
    async def by_identity(self, order_id: Identity) -> Order | None: ...

    @abstractmethod
    def add(self, order: Order) -> None: ...
