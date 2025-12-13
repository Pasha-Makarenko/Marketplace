from dishka import AsyncContainer, make_async_container
from main.config import Config, DbConfig
from main.di.providers import DbProvider


def setup_ioc_container(config: Config) -> AsyncContainer:
    container = make_async_container(
        DbProvider(),
        context={
            Config: config,
            DbConfig: config.db,
        },
    )
    return container
