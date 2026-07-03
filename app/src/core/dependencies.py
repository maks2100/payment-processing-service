import typing as t
import logging
from collections.abc import AsyncGenerator

from fastapi import Depends, Response
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.clients import HttpClient
from src.core.broker.rabbit import get_broker, RabbitBroker
from src.core.db.manager import async_db_manager

logger = logging.getLogger(__name__)


async def get_async_db_session() -> AsyncGenerator[AsyncSession, None]:
    try:
        async with async_db_manager.session() as session:
            yield session
    except SQLAlchemyError:
        logger.exception("Async DB operation failed")
        raise


def add_no_cache_headers(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["Surrogate-Control"] = "no-store"


def get_http_client() -> HttpClient:
    return HttpClient()

AsyncDbSessionDI = t.Annotated[AsyncSession, Depends(get_async_db_session)]
NoCacheHeadersDI = t.Annotated[None, Depends(add_no_cache_headers)]
RabbitBrokerDI = t.Annotated[RabbitBroker, Depends(get_broker)]
HttpClientDI = t.Annotated[HttpClient, Depends(get_http_client)]
