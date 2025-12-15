from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, status

from marketplace.application.category.create import (
    CategoryCreationRequest,
    CreateCategory,
)
from marketplace.application.category.delete import (
    DeleteCategory,
    DeleteCategoryRequest,
)
from marketplace.application.category.get import (
    GetCategory,
    GetCategoryRequest,
)
from marketplace.application.category.list import ListCategories
from marketplace.domain.entities.category.category import Category

category_router = APIRouter(
    prefix="/categories",
    tags=["categories"],
    route_class=DishkaRoute,
)


@category_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreationRequest,
    create_command: FromDishka[CreateCategory],
) -> dict[str, int]:
    category_id = await create_command(data)
    return {"id": category_id}


@category_router.get("/", status_code=status.HTTP_200_OK)
async def list_categories(
    list_query: FromDishka[ListCategories],
) -> list[Category]:
    return await list_query()


@category_router.get("/{category_id}", status_code=status.HTTP_200_OK)
async def get_category(
    category_id: int,
    get_query: FromDishka[GetCategory],
) -> Category:
    return await get_query(GetCategoryRequest(category_id=category_id))


@category_router.delete(
    "/{category_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_category(
    category_id: int,
    delete_command: FromDishka[DeleteCategory],
) -> None:
    await delete_command(DeleteCategoryRequest(category_id=category_id))
