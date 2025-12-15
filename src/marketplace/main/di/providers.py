from typing import AsyncIterable

from dishka import AnyOf, Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)

from marketplace.application.category.create import CreateCategory
from marketplace.application.category.delete import DeleteCategory
from marketplace.application.category.get import GetCategory
from marketplace.application.category.list import ListCategories
from marketplace.application.common.id_provider import IdProvider
from marketplace.application.common.transaction_manager import (
    TransactionManager,
)
from marketplace.application.product.create import CreateProduct
from marketplace.application.product.delete import DeleteProduct
from marketplace.application.product.get import GetProduct
from marketplace.application.product.list import ListProducts
from marketplace.application.product.update import UpdateProduct
from marketplace.application.seller.create import CreateSeller
from marketplace.application.seller.get import GetSeller
from marketplace.application.seller.list import ListSellers
from marketplace.application.seller.update import UpdateSeller
from marketplace.application.user.register import RegisterUserCommand
from marketplace.domain.entities.category.repository import CategoryRepository
from marketplace.domain.entities.product.repository import ProductRepository
from marketplace.domain.entities.seller.factory import SellerFactory
from marketplace.domain.entities.seller.repository import SellerRepository
from marketplace.domain.entities.user.factory import UserFactory
from marketplace.domain.entities.user.hasher import PasswordHasher
from marketplace.domain.entities.user.repository import UserRepository
from marketplace.infrastructure.auth import Auther
from marketplace.infrastructure.hasher import Hasher
from marketplace.infrastructure.persistence.category_repo import (
    SQLCategoryRepository,
)
from marketplace.infrastructure.persistence.product_repo import (
    SQLProductRepository,
)
from marketplace.infrastructure.persistence.seller_repo import (
    SQLSellerRepository,
)
from marketplace.infrastructure.persistence.session_repo import (
    SQLSessionRepository,
)
from marketplace.infrastructure.persistence.setup import (
    create_engine,
    create_session_pool,
)
from marketplace.infrastructure.persistence.transaction_manager import (
    SQLTransactionManager,
)
from marketplace.infrastructure.persistence.user_repo import SQLUserRepository
from marketplace.infrastructure.session_id_provider import (
    FastAPISessionIDGetter,
    HTTPIdentityProvider,
    SessionIDGetter,
)
from marketplace.infrastructure.session_manager import (
    FastAPISessionManager,
    HTTPSessionManager,
)
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
    http_identity_provider = provide(
        source=HTTPIdentityProvider, provides=IdProvider, scope=Scope.REQUEST
    )
    session_id_getter = provide(
        source=FastAPISessionIDGetter,
        provides=SessionIDGetter,
        scope=Scope.REQUEST,
    )
    session_repo = provide(source=SQLSessionRepository, scope=Scope.REQUEST)

    http_session_manager = provide(
        source=HTTPSessionManager, scope=Scope.REQUEST
    )
    fastapi_session_manager = provide(
        source=FastAPISessionManager, scope=Scope.REQUEST
    )


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


class CategoryProvider(Provider):
    category_repo = provide(
        scope=Scope.REQUEST,
        source=SQLCategoryRepository,
        provides=AnyOf[CategoryRepository, SQLCategoryRepository],
    )
    create_category = provide(scope=Scope.REQUEST, source=CreateCategory)
    delete_category = provide(scope=Scope.REQUEST, source=DeleteCategory)
    get_category = provide(scope=Scope.REQUEST, source=GetCategory)
    list_categories = provide(scope=Scope.REQUEST, source=ListCategories)


class SellerProvider(Provider):
    seller_repo = provide(
        scope=Scope.REQUEST,
        source=SQLSellerRepository,
        provides=AnyOf[SellerRepository, SQLSellerRepository],
    )
    factory = provide(scope=Scope.REQUEST, source=SellerFactory)
    create_seller = provide(scope=Scope.REQUEST, source=CreateSeller)
    update_seller = provide(scope=Scope.REQUEST, source=UpdateSeller)
    get_seller = provide(scope=Scope.REQUEST, source=GetSeller)
    list_sellers = provide(scope=Scope.REQUEST, source=ListSellers)


class ProductProvider(Provider):
    product_repo = provide(
        scope=Scope.REQUEST,
        source=SQLProductRepository,
        provides=AnyOf[ProductRepository, SQLProductRepository],
    )
    create_product = provide(scope=Scope.REQUEST, source=CreateProduct)
    update_product = provide(scope=Scope.REQUEST, source=UpdateProduct)
    delete_product = provide(scope=Scope.REQUEST, source=DeleteProduct)
    list_products = provide(scope=Scope.REQUEST, source=ListProducts)
    get_product = provide(scope=Scope.REQUEST, source=GetProduct)
