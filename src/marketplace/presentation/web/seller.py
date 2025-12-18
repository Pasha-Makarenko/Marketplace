from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Query, status

from marketplace.application.seller.create import CreateSeller
from marketplace.application.seller.get import GetSeller, GetSellerRequest
from marketplace.application.seller.list import ListSellers, ListSellersRequest
from marketplace.application.seller.update import (
    UpdateSeller,
    UpdateSellerRequest,
)
from marketplace.domain.entities.seller.factory import CreateSellerRequest
from marketplace.domain.entities.seller.seller import Seller
from marketplace.infrastructure.queries.seller_analytics import (
    SellerAnalyticsQuery,
)

seller_router = APIRouter(
    prefix="/sellers",
    tags=["sellers"],
    route_class=DishkaRoute,
)


@seller_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_seller(
    data: CreateSellerRequest,
    create_command: FromDishka[CreateSeller],
) -> dict[str, int]:
    seller_id = await create_command(data)
    return {"id": seller_id}


@seller_router.get("/", status_code=status.HTTP_200_OK)
async def list_sellers(
    list_query: FromDishka[ListSellers],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[Seller]:
    return await list_query(ListSellersRequest(limit=limit, offset=offset))


@seller_router.get("/analytics/top", status_code=status.HTTP_200_OK)
async def get_top_sellers(
    analytics: FromDishka[SellerAnalyticsQuery],
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
) -> list[dict[str, object]]:
    return await analytics.get_top_sellers(limit=limit)


@seller_router.get("/{seller_id}", status_code=status.HTTP_200_OK)
async def get_seller(
    seller_id: int,
    get_query: FromDishka[GetSeller],
) -> dict[str, object]:
    seller = await get_query(GetSellerRequest(seller_id=seller_id))
    return {
        "id": seller.identity.value,
        "user_id": seller.user_id.value,
        "store_name": seller.store_name,
        "store_logs": seller.store_logs,
        "contact_info": seller.contact_info,
        "return_policy": seller.return_policy,
        "delivery_terms": seller.delivery_terms,
        "is_active": seller.is_active,
    }


@seller_router.patch("/{seller_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_seller(
    seller_id: int,
    data: UpdateSellerRequest,
    update_command: FromDishka[UpdateSeller],
) -> None:
    request = UpdateSellerRequest(
        seller_id=seller_id,
        store_name=data.store_name,
        contact_info=data.contact_info,
        return_policy=data.return_policy,
        delivery_terms=data.delivery_terms,
    )
    await update_command(request)
