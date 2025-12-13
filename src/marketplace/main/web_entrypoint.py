from contextlib import asynccontextmanager
from typing import AsyncContextManager, AsyncIterator, Callable

from dishka import AsyncContainer
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from cryptoapp.main.config import load_config
from cryptoapp.main.di.setup import setup_ioc_container
from cryptoapp.main.taskiq_entry.broker import create_broker
from cryptoapp.main.web_errors import register_exception_handlers


def create_app(container: AsyncContainer) -> FastAPI:
    app = FastAPI(
        default_response_class=ORJSONResponse,
        openapi_prefix="/api"
    )

    origins_dev = [
        "http://localhost",
        "http://127.0.0.1",
        "http://localhost:4242",
        "http://127.0.0.1:4242",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins_dev,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    init_routers(app)
    register_exception_handlers(app)
    setup_logging()

    setup_dishka(container=container, app=app)

    return app

def main() -> FastAPI:
    config = load_config()
    broker = create_broker(config)
    container = setup_ioc_container(config=config, broker=broker)
    app = create_app(broker=broker, container=container)
    return app