from decimal import Decimal
from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Query, status
from pydantic import BaseModel

from marketplace.application.product.create import CreateProduct
from marketplace.application.product.delete import (
    DeleteProduct,
    DeleteProductRequest,
)
from marketplace.application.product.get import GetProduct, GetProductRequest
from marketplace.application.product.list import (
    ListProducts,
    ListProductsRequest,
)
from marketplace.application.product.update import (
    UpdateProduct,
    UpdateProductRequest,
)
from marketplace.domain.entities.product.factory import CreateProductRequest
from marketplace.domain.entities.product.product import Product
from marketplace.infrastructure.queries.product_analytics import (
    ProductAnalyticsQuery,
)

product_router = APIRouter(
    prefix="/products",
    tags=["products"],
    route_class=DishkaRoute,
)


class UpdateProductPayload(BaseModel):
    name: str | None = None
    description: str | None = None
    price: Decimal | None = None
    discount: int | None = None
    stock_quantity: int | None = None
    category_id: int | None = None


def _product_to_dict(product: Product) -> dict[str, object]:
    return {
        "id": product.identity.value,
        "name": product.name,
        "description": product.description,
        "price": float(product.price),
        "discount": product.discount,
        "stock_quantity": product.stock_quantity,
        "owner_id": product.owner_id.value,
        "category_id": product.category_id.value,
        "is_active": product.is_active,
    }


@product_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_product(
    data: CreateProductRequest,
    create_command: FromDishka[CreateProduct],
) -> dict[str, int]:
    product_id = await create_command(data)
    return {"id": product_id}


@product_router.get("/", status_code=status.HTTP_200_OK)
async def list_products(
    list_query: FromDishka[ListProducts],
    category_id: Annotated[int | None, Query()] = None,
    min_price: Annotated[Decimal | None, Query()] = None,
    max_price: Annotated[Decimal | None, Query()] = None,
    is_active: Annotated[bool, Query()] = True,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[dict[str, object]]:
    products = await list_query(
        ListProductsRequest(
            category_id=category_id,
            min_price=min_price,
            max_price=max_price,
            is_active=is_active,
            limit=limit,
            offset=offset,
        )
    )
    return [_product_to_dict(p) for p in products]


@product_router.get("/analytics/top-rated", status_code=status.HTTP_200_OK)
async def get_top_rated_products(
    analytics: FromDishka[ProductAnalyticsQuery],
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
) -> list[dict[str, object]]:
    return await analytics.get_top_rated_products(limit=limit)


@product_router.get("/analytics/low-stock", status_code=status.HTTP_200_OK)
async def get_low_stock_products(
    analytics: FromDishka[ProductAnalyticsQuery],
    threshold: Annotated[int, Query(ge=1)] = 5,
) -> list[dict[str, object]]:
    return await analytics.get_low_stock_products(threshold=threshold)


@product_router.get("/{product_id}", status_code=status.HTTP_200_OK)
async def get_product(
    product_id: int,
    get_query: FromDishka[GetProduct],
) -> dict[str, object]:
    product = await get_query(GetProductRequest(product_id=product_id))
    return _product_to_dict(product)


@product_router.patch("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_product(
    product_id: int,
    data: UpdateProductPayload,
    update_command: FromDishka[UpdateProduct],
) -> None:
    request = UpdateProductRequest(
        product_id=product_id,
        name=data.name,
        description=data.description,
        price=data.price,
        discount=data.discount,
        stock_quantity=data.stock_quantity,
        category_id=data.category_id,
    )
    await update_command(request)


@product_router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    delete_command: FromDishka[DeleteProduct],
) -> None:
    await delete_command(DeleteProductRequest(product_id=product_id))
