from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, status

from marketplace.application.user.register import RegisterUserCommand
from marketplace.domain.entities.user.factory import CreateUserRequest

user_router = APIRouter(
    prefix="/users",
    tags=["users"],
    route_class=DishkaRoute,
)


@user_router.post("/", status_code=status.HTTP_201_CREATED)
async def register_user(
    data: CreateUserRequest,
    command: FromDishka[RegisterUserCommand],
) -> dict[str, int]:
    user_id = await command.execute(
        CreateUserRequest(
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            password=data.password,
            phone=data.phone,
        )
    )
    return {"id": user_id}


@user_router.get("/me")
async def me() -> dict[str, str]:
    return {"username": "me"}
