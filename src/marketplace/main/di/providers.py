from typing import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)

from marketplace.infrastructure.persistence.setup import (
    create_engine,
    create_session_pool,
)
from marketplace.main.config import DbConfig


class DbProvider(Provider):
    @provide(scope=Scope.APP)
    def engine(self, db_config: DbConfig) -> AsyncEngine:
        return create_engine(db_config)

    @provide(scope=Scope.APP)
    async def session_pool(
        self, engine: AsyncEngine
    ) -> async_sessionmaker[AsyncSession]:
        return create_session_pool(engine)

    @provide(scope=Scope.REQUEST)
    async def session(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AsyncSession]:
        async with session_factory() as session:
            yield session
