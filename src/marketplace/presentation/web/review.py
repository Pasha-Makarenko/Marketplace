from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Query, status

from marketplace.application.review.analytics import (
    GetRecentReviews,
    GetRecentReviewsRequest,
)
from marketplace.application.review.create import CreateReview
from marketplace.application.review.list import ListReviews, ListReviewsRequest
from marketplace.domain.entities.review.factory import CreateReviewRequest
from marketplace.domain.entities.review.review import Review

review_router = APIRouter(
    prefix="/reviews",
    tags=["reviews"],
    route_class=DishkaRoute,
)


@review_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_review(
    data: CreateReviewRequest,
    create_command: FromDishka[CreateReview],
) -> dict[str, int]:
    review_id = await create_command(data)
    return {"id": review_id}


@review_router.get("/", status_code=status.HTTP_200_OK)
async def list_reviews(
    product_id: int,
    list_query: FromDishka[ListReviews],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[Review]:
    return await list_query(
        ListReviewsRequest(
            product_id=product_id,
            limit=limit,
            offset=offset,
        )
    )


@review_router.get("/recent", status_code=status.HTTP_200_OK)
async def get_recent_reviews(
    list_query: FromDishka[GetRecentReviews],
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
) -> list[Review]:
    return await list_query(GetRecentReviewsRequest(limit=limit))
