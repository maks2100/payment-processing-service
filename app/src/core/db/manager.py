import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

logger = logging.getLogger(__name__)


class DBNotInitializedError(RuntimeError):
    def __init__(self) -> None:
        super().__init__("DB not initialized")


class AsyncDBManager:
    def __init__(self) -> None:
        self._engine: AsyncEngine | None = None
        self._sessionmaker: async_sessionmaker[AsyncSession] | None = None

    async def init(  # noqa: PLR0913
        self,
        url: str,
        *,
        echo: bool = False,
        pool_size: int,
        max_overflow: int,
        pool_pre_ping: bool,
        pool_timeout: int,
        pool_recycle: int,
    ) -> None:
        if self._engine is not None:
            return

        engine = create_async_engine(
            url=url,
            echo=echo,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_pre_ping=pool_pre_ping,
            pool_timeout=pool_timeout,
            pool_recycle=pool_recycle,
        )

        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
        except SQLAlchemyError:
            await engine.dispose()
            raise

        self._engine = engine
        self._sessionmaker = async_sessionmaker(
            bind=self._engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )

    async def dispose(self) -> None:
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._sessionmaker = None

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        if self._sessionmaker is None:
            raise DBNotInitializedError

        async with self._sessionmaker() as session:
            yield session


async_db_manager = AsyncDBManager()
