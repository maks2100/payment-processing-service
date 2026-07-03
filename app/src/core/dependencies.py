import typing as t
import logging
from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, Header, Response
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.clients import HttpClient
from src.core.config import get_settings
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


def get_api_key(x_api_key: str = Header(alias="X-API-KEY")):
    settings = get_settings()
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key


AsyncDbSessionDI = t.Annotated[AsyncSession, Depends(get_async_db_session)]
NoCacheHeadersDI = t.Annotated[None, Depends(add_no_cache_headers)]
RabbitBrokerDI = t.Annotated[RabbitBroker, Depends(get_broker)]
HttpClientDI = t.Annotated[HttpClient, Depends(get_http_client)]
AuthDI = t.Annotated[str, Depends(get_api_key)]