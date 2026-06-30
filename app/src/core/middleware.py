from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from src.core.config import Settings, get_settings


def setup_cors_middleware(app: FastAPI, settings: Settings) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )


def setup_trusted_host_middleware(app: FastAPI, settings: Settings) -> None:
    if not settings.debug:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.trusted_hosts,
        )


def setup_middleware(app: FastAPI) -> None:
    settings = get_settings()

    # Processing order: from bottom to top.
    setup_trusted_host_middleware(app, settings)
    setup_cors_middleware(app, settings)
