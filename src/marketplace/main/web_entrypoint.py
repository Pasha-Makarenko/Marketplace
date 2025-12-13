from dishka import AsyncContainer
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from marketplace.main.config import load_config
from marketplace.main.di.setup import setup_ioc_container
from marketplace.main.init_routers import init_routers
from marketplace.main.log import setup_logging
from marketplace.main.web_errors import register_exception_handlers


def create_app(container: AsyncContainer) -> FastAPI:
    app = FastAPI(default_response_class=ORJSONResponse, root_path="/api")

    app.add_middleware(
        CORSMiddleware,
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
    container = setup_ioc_container(config=config)
    app = create_app(container=container)
    return app
