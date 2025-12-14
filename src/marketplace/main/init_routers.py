from fastapi import FastAPI

from marketplace.presentation.web.auth import auth_router
from marketplace.presentation.web.root import root_router
from marketplace.presentation.web.user import user_router


def init_routers(app: FastAPI) -> None:
    app.include_router(root_router)
    app.include_router(user_router)
    app.include_router(auth_router)
