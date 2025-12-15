from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.user.repository import UserRepository
from marketplace.domain.entities.user.user import User
from marketplace.infrastructure.persistence.base_repo import Repository


class SQLUserRepository(Repository[User], UserRepository):
    model = User

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def by_identity(self, user_id: Identity) -> User | None:
        return await self._session.get(self.model, user_id.value)

    async def by_email(self, email: str) -> User | None:
        stmt = select(self.model).where(
            self.model.email == email  # type: ignore
        )
        return await self._session.scalar(stmt)

    async def is_email_unique(self, email: str) -> bool:
        stmt = select(self.model).where(
            self.model.email == email  # type: ignore
        )
        return (await self._session.scalar(stmt)) is None
