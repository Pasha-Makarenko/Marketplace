from sqlalchemy.ext.asyncio import AsyncSession

from marketplace.application.common.transaction_manager import (
    TransactionManager,
)


class SQLTransactionManager(TransactionManager):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def commit(self) -> None:
        await self.session.commit()

    async def flush(self) -> None:
        await self.session.flush()
