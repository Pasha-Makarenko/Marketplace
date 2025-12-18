from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Query, status

from marketplace.application.rating.analytics import (
    GetProductAverageRating,
    GetProductAverageRatingRequest,
    GetRatingDistribution,
    GetRatingDistributionRequest,
)
from marketplace.application.rating.create import CreateRating
from marketplace.application.rating.list import ListRatings, ListRatingsRequest
from marketplace.domain.entities.rating.factory import CreateRatingRequest
from marketplace.domain.entities.rating.rating import Rating

rating_router = APIRouter(
    prefix="/ratings",
    tags=["ratings"],
    route_class=DishkaRoute,
)


@rating_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_rating(
    data: CreateRatingRequest,
    create_command: FromDishka[CreateRating],
) -> dict[str, int]:
    rating_id = await create_command(data)
    return {"id": rating_id}


@rating_router.get("/", status_code=status.HTTP_200_OK)
async def list_ratings(
    product_id: int,
    list_query: FromDishka[ListRatings],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[Rating]:
    return await list_query(
        ListRatingsRequest(
            product_id=product_id,
            limit=limit,
            offset=offset,
        )
    )


@rating_router.get("/distribution", status_code=status.HTTP_200_OK)
async def get_rating_distribution(
    product_id: int,
    query: FromDishka[GetRatingDistribution],
) -> dict[int, int]:
    return await query(GetRatingDistributionRequest(product_id=product_id))


@rating_router.get("/average", status_code=status.HTTP_200_OK)
async def get_average_rating(
    product_id: int,
    query: FromDishka[GetProductAverageRating],
) -> dict[str, float]:
    avg = await query(GetProductAverageRatingRequest(product_id=product_id))
    return {"average_rating": avg}
