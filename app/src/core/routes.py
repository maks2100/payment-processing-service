from fastapi import APIRouter
from fastapi.responses import JSONResponse

from src.payments.routes import api_router as payments_router

api_router = APIRouter()

api_router.include_router(payments_router)


@api_router.get(
    "/healthz",
    summary="Health check endpoint.",
)
async def healthz() -> JSONResponse:
    return JSONResponse(
        status_code=200,
        content={"status": "ok", "message": "Service is healthy"},
    )
