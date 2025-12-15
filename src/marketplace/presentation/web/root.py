from fastapi import APIRouter

root_router = APIRouter()


@root_router.get("/health")
async def root() -> dict[str, str]:
    return {"message": "success"}
