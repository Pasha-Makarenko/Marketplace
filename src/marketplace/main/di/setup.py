from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import FastapiProvider

from marketplace.main.config import Config, DbConfig
from marketplace.main.di.providers import (
    CategoryProvider,
    DbProvider,
    OrderProvider,
    ProductProvider,
    RatingProvider,
    ReviewProvider,
    SellerProvider,
    UserProvider,
)


def setup_ioc_container(config: Config) -> AsyncContainer:
    container = make_async_container(
        FastapiProvider(),
        DbProvider(),
        UserProvider(),
        CategoryProvider(),
        SellerProvider(),
        ProductProvider(),
        OrderProvider(),
        ReviewProvider(),
        RatingProvider(),
        context={
            Config: config,
            DbConfig: config.db,
        },
    )
    return container
