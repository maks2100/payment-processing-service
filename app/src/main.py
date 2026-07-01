from fastapi import FastAPI

from src.core.broker.manager import rabbit_router
from src.core.config import get_settings
from src.core.events import lifespan
from src.core.exception_handlers import setup_exception_handlers
from src.core.middleware import setup_middleware
from src.core.responses import ErrorResponse
from src.core.routes import api_router


def create_application() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        root_path=settings.app_root_path,
        lifespan=lifespan,
        openapi_url=f"{settings.api_prefix}/openapi.json" if settings.docs_enabled else None,
        docs_url=f"{settings.api_prefix}/docs" if settings.docs_enabled else None,
        redoc_url=f"{settings.api_prefix}/redoc" if settings.docs_enabled else None,
        responses={
            422: {"description": "Validation Error", "model": ErrorResponse},
            500: {"description": "Internal Server Error", "model": ErrorResponse},
        },
    )

    setup_middleware(application)

    setup_exception_handlers(application)

    application.include_router(api_router, prefix=settings.api_prefix)
    application.include_router(rabbit_router)
    return application


app = create_application()
