from fastapi import FastAPI

from marketplace.presentation.web.auth import auth_router
from marketplace.presentation.web.category import category_router
from marketplace.presentation.web.order import order_router
from marketplace.presentation.web.product import product_router
from marketplace.presentation.web.root import root_router
from marketplace.presentation.web.seller import seller_router
from marketplace.presentation.web.user import user_router


def init_routers(app: FastAPI) -> None:
    app.include_router(root_router)
    app.include_router(user_router)
    app.include_router(auth_router)
    app.include_router(product_router)
    app.include_router(category_router)
    app.include_router(seller_router)
    app.include_router(order_router)
