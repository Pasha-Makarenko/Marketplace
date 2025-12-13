from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

user_router = APIRouter(
    prefix="/users",
    tags=["users"],
    route_class=DishkaRoute,
)


@user_router.get("/me")
async def me() -> dict[str, str]:
    return {"username": "me"}
