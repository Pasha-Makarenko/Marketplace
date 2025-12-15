from typing import Any, cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import QueryableAttribute, selectinload

from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.order.order import Order
from marketplace.domain.entities.order.repository import OrderRepository
from marketplace.infrastructure.persistence.base_repo import Repository
from marketplace.infrastructure.persistence.tables.orders import orders_table


class SQLOrderRepository(Repository[Order], OrderRepository):
    model = Order

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def by_identity(self, order_id: Identity) -> Order | None:
        items_attr = cast(QueryableAttribute[Any], Order.items)
        stmt = (
            select(self.model)
            .options(selectinload(items_attr))
            .where(orders_table.c.order_id == order_id.value)
        )
        result = await self._session.scalars(stmt)
        return result.first()

    def add(self, order: Order) -> None:
        self._session.add(order)
