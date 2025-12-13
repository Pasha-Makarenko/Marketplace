from domain.exceptions import BaseNotFound, DomainError
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from starlette.requests import Request


async def business_logic_error_handler(
    request: Request, exception: Exception
) -> ORJSONResponse:
    return ORJSONResponse(status_code=409, content={"detail": str(exception)})


async def resource_not_found(
    request: Request, exception: Exception
) -> ORJSONResponse:
    return ORJSONResponse(status_code=404, content={"detail": str(exception)})


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DomainError, business_logic_error_handler)
    app.add_exception_handler(BaseNotFound, resource_not_found)
