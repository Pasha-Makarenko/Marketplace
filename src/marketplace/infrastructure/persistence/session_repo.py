from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from marketplace.domain.entities.session import Session
from marketplace.infrastructure.persistence.base_repo import Repository
from marketplace.infrastructure.persistence.tables.sessions import (
    sessions_table,
)


class SQLSessionRepository(Repository[Session]):
    model = Session

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def delete_session(self, session_id: str) -> None:
        await self._session.execute(
            delete(sessions_table).where(
                sessions_table.c.session_id == session_id
            )
        )

    async def by_identity(self, session_id: str) -> Session | None:
        return await self._session.get(Session, session_id)
