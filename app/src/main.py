import logging

from fastapi import FastAPI

from src.core.broker.rabbit import router as rabbit_router
from src.core.config import get_settings
from src.core.events import lifespan
from src.core.exception_handlers import setup_exception_handlers
from src.core.middleware import setup_middleware
from src.core.responses import ErrorResponse
from src.core.routes import api_router, health_router

logger = logging.getLogger(__name__)


def create_application() -> FastAPI:
    settings = get_settings()

    docs_enabled = settings.docs_enabled and not settings.include_consumer

    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        root_path=settings.app_root_path,
        lifespan=lifespan,
        openapi_url=f"{settings.api_prefix}/openapi.json" if docs_enabled else None,
        docs_url=f"{settings.api_prefix}/docs" if docs_enabled else None,
        redoc_url=f"{settings.api_prefix}/redoc" if docs_enabled else None,
        responses={
            422: {"description": "Validation Error", "model": ErrorResponse},
            500: {"description": "Internal Server Error", "model": ErrorResponse},
        },
    )

    setup_middleware(application)

    setup_exception_handlers(application)

    application.include_router(health_router, prefix=settings.api_prefix)
    if not settings.include_consumer:
        application.include_router(api_router, prefix=settings.api_prefix)

    application.include_router(rabbit_router)

    role = "consumer" if settings.include_consumer else "api"
    logger.info("Starting service in '%s' role (INCLUDE_CONSUMER=%s)", role, settings.include_consumer)

    return application


app = create_application()
