import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.broker.manager import declare_queues, rabbit_router
from src.core.config import Settings, get_settings
from src.core.db.manager import async_db_manager
from src.core.logging import setup_logging

logger = logging.getLogger(__name__)


async def init_db(settings: Settings) -> None:
    logger.info("Initializing DB connection...")
    try:
        await async_db_manager.init(
            url=str(settings.db.async_url),
            echo=settings.debug,
            pool_size=settings.db.pool_size,
            max_overflow=settings.db.pool_max_overflow,
            pool_pre_ping=settings.db.pool_pre_ping,
            pool_timeout=settings.db.pool_timeout,
            pool_recycle=settings.db.pool_recycle,
        )
        logger.info("DB connection initialized successfully")
    except Exception:
        logger.exception("Error during initializing DB connection")
        raise


async def close_db() -> None:
    logger.info("Closing DB connections...")
    try:
        await async_db_manager.dispose()
        logger.info("DB connections closed successfully")
    except Exception:
        logger.exception("Error during closing DB connection")


async def startup_event() -> None:
    settings = get_settings()

    setup_logging(settings)

    logger.info("Starting up application...")

    await init_db(settings)

    logger.info("Application startup completed")


async def shutdown_event() -> None:
    logger.info("Shutting down application...")

    await close_db()

    logger.info("Application shutdown completed")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await startup_event()

    async with rabbit_router.lifespan_context(app):
        await declare_queues(rabbit_router.broker)
        yield

    await shutdown_event()
