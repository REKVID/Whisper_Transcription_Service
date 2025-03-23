from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine

from .models import Base

import logging

logger = logging.getLogger(__name__)

class Database:
    # асинный движок базы данных 
    # асинхронная алхимия вообще пздц нихуя не понятно. 
    # Изначально делал с синхронной алхимией,было все просто
    def __init__(self, db_url: str) -> None:
        self._engine = create_async_engine(
            db_url.replace('sqlite://', 'sqlite+aiosqlite://'),
            echo=True,
        )
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )

    @property
    def engine(self) -> AsyncEngine:
        return self._engine

    async def create_database(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    # тоже стандартная залупа
    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        session: AsyncSession = self._session_factory()
        try:
            yield session
        except Exception:
            logger.exception("Session rollback because of exception")
            await session.rollback()
            raise
        finally:
            await session.close()
