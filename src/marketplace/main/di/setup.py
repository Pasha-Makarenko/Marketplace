from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import FastapiProvider

from marketplace.main.config import Config, DbConfig
from marketplace.main.di.providers import DbProvider, UserProvider


def setup_ioc_container(config: Config) -> AsyncContainer:
    container = make_async_container(
        FastapiProvider(),
        DbProvider(),
        UserProvider(),
        context={
            Config: config,
            DbConfig: config.db,
        },
    )
    return container
