from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, status

from marketplace.application.feedback.leave_feedback import (
    LeaveFeedback,
    LeaveFeedbackRequest,
)

feedback_router = APIRouter(
    prefix="/feedback",
    tags=["feedback"],
    route_class=DishkaRoute,
)


@feedback_router.post("/", status_code=status.HTTP_201_CREATED)
async def leave_feedback(
    data: LeaveFeedbackRequest,
    command: FromDishka[LeaveFeedback],
) -> dict[str, str]:
    await command(data)
    return {"status": "success", "message": "Feedback submitted successfully"}
