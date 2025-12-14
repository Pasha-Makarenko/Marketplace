from typing import AsyncIterable

from dishka import Provider, Scope, provide, AnyOf
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)

from marketplace.application.common.transaction_manager import (
    TransactionManager,
)
from marketplace.application.user.register import RegisterUserCommand
from marketplace.domain.entities.user.factory import UserFactory
from marketplace.domain.entities.user.hasher import PasswordHasher
from marketplace.domain.entities.user.repository import UserRepository
from marketplace.infrastructure.auth import Auther
from marketplace.infrastructure.hasher import Hasher
from marketplace.infrastructure.persistence.setup import (
    create_engine,
    create_session_pool,
)
from marketplace.infrastructure.persistence.transaction_manager import (
    SQLTransactionManager,
)
from marketplace.infrastructure.persistence.user_repo import SQLUserRepository
from marketplace.main.config import DbConfig


class UserProvider(Provider):
    user_repo = provide(
        scope=Scope.REQUEST,
        source=SQLUserRepository,
        provides=AnyOf[UserRepository, SQLUserRepository],
    )
    hasher = provide(
        scope=Scope.APP,
        source=Hasher,
        provides=PasswordHasher,
    )
    factory = provide(scope=Scope.REQUEST, source=UserFactory)
    register = provide(scope=Scope.REQUEST, source=RegisterUserCommand)
    auther = provide(scope=Scope.REQUEST, source=Auther)



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

    transaction_manager = provide(
        source=SQLTransactionManager,
        provides=TransactionManager,
        scope=Scope.REQUEST,
    )
