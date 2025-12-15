from __future__ import annotations

from decimal import Decimal

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from marketplace.application.order.cancel_order import (
    CancelOrderCommand,
    CancelOrderRequest,
)
from marketplace.application.order.checkout_order import (
    CheckoutOrderCommand,
    CheckoutOrderItem,
    CheckoutOrderRequest,
)
from marketplace.application.order.fulfill_order import (
    FulfillOrderCommand,
    FulfillOrderRequest,
)
from marketplace.application.order.pay_order import (
    PayOrderCommand,
    PayOrderRequest,
)
from marketplace.infrastructure.queries.order_queries import (
    DailyRevenueQuery,
    OrderStatusStatsQuery,
    UserOrdersQuery,
)

order_router = APIRouter(
    prefix="/orders",
    tags=["orders"],
    route_class=DishkaRoute,
)


class CreateOrderPayload(BaseModel):
    items: list["CheckoutItemPayload"]


class CheckoutItemPayload(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    price_at_purchase: Decimal = Field(gt=0)
    title: str


@order_router.post("/checkout", status_code=status.HTTP_201_CREATED)
async def checkout_order(
    payload: CreateOrderPayload,
    command: FromDishka[CheckoutOrderCommand],
) -> dict[str, int]:
    order_id = await command.execute(
        CheckoutOrderRequest(
            items=[
                CheckoutOrderItem(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price_at_purchase=item.price_at_purchase,
                    title=item.title,
                )
                for item in payload.items
            ]
        )
    )
    return {"id": order_id}


class PayPayload(BaseModel):
    transaction_id: str


@order_router.post("/{order_id}/pay", status_code=status.HTTP_204_NO_CONTENT)
async def pay_order(
    order_id: int,
    payload: PayPayload,
    command: FromDishka[PayOrderCommand],
) -> None:
    await command.execute(
        PayOrderRequest(
            order_id=order_id,
            transaction_id=payload.transaction_id,
        )
    )


class FulfillPayload(BaseModel):
    tracking_number: str | None = None


@order_router.post(
    "/{order_id}/fulfill", status_code=status.HTTP_204_NO_CONTENT
)
async def fulfill_order(
    order_id: int,
    payload: FulfillPayload,
    command: FromDishka[FulfillOrderCommand],
) -> None:
    await command.execute(
        FulfillOrderRequest(
            order_id=order_id,
            tracking_number=payload.tracking_number,
        )
    )


@order_router.post(
    "/{order_id}/cancel", status_code=status.HTTP_204_NO_CONTENT
)
async def cancel_order(
    order_id: int,
    command: FromDishka[CancelOrderCommand],
) -> None:
    await command.execute(
        CancelOrderRequest(
            order_id=order_id,
        )
    )


@order_router.get("/me", status_code=status.HTTP_200_OK)
async def my_orders(
    query: FromDishka[UserOrdersQuery],
) -> list[dict[str, object]]:
    return await query.fetch()


@order_router.get("/stats/statuses", status_code=status.HTTP_200_OK)
async def status_stats(
    query: FromDishka[OrderStatusStatsQuery],
) -> dict[str, int]:
    return await query.fetch()


@order_router.get("/stats/daily-revenue", status_code=status.HTTP_200_OK)
async def daily_revenue(
    query: FromDishka[DailyRevenueQuery],
    days: int = 30,
) -> list[dict[str, object]]:
    return await query.fetch(days=days)
