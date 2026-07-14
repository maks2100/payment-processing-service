from fastapi import APIRouter
from fastapi.responses import JSONResponse

from src.core.config import get_settings
from src.payments.routes import api_router as payments_router

health_router = APIRouter()


@health_router.get(
    "/healthz",
    summary="Health check endpoint.",
)
async def healthz() -> JSONResponse:
    settings = get_settings()
    role = "consumer" if settings.include_consumer else "api"

    return JSONResponse(
        status_code=200,
        content={"status": "ok", "message": "Service is healthy", "role": role},
    )

api_router = APIRouter()
api_router.include_router(payments_router)
