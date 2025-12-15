from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Response, status
from starlette.requests import Request

from marketplace.application.common.transaction_manager import (
    TransactionManager,
)
from marketplace.infrastructure.auth import Auther, LoginAuthRequest
from marketplace.infrastructure.session_manager import FastAPISessionManager

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    route_class=DishkaRoute,
)


@auth_router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    data: LoginAuthRequest,
    request: Request,
    response: Response,
    transaction_manager: FromDishka[TransactionManager],
    auth_service: FromDishka[Auther],
    session_manager: FromDishka[FastAPISessionManager],
) -> dict[str, str]:
    user_id = await auth_service.authenticate(
        LoginAuthRequest(email=data.email, password=data.password)
    )
    await session_manager.init_session(
        user_id,
        response=response,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )
    await transaction_manager.commit()
    return {"message": "You have successfully logged in."}


@auth_router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    request: Request,
    response: Response,
    transaction_manager: FromDishka[TransactionManager],
    session_manager: FromDishka[FastAPISessionManager],
) -> dict[str, str]:
    await session_manager.invalidate_session(
        request=request, response=response
    )
    await transaction_manager.commit()
    return {"message": "You have been logged out successfully."}
