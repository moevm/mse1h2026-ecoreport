from typing import AsyncIterator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from contextlib import asynccontextmanager
from reports.core.config import settings

class Database:
    def __init__(self, url: str):
        self._engine = create_async_engine(
            url,
            pool_size=settings.MIN_POOL_SIZE,
            max_overflow=settings.MAX_POOL_SIZE - settings.MIN_POOL_SIZE,
            pool_pre_ping=True,
        )
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False
        )

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        session = self._session_factory()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()