from fastapi import APIRouter
from fastapi.responses import JSONResponse

api_router = APIRouter()


@api_router.get("/healthz", tags=["health"])
async def healthz():
    """
    Health check endpoint.
    Returns 200 OK if the application is alive.
    """
    return JSONResponse(
        status_code=200,
        content={"status": "ok", "message": "Service is healthy"},
    )
