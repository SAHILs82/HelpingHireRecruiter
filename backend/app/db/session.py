from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings

from app.db import models as _models  # noqa: F401  # registers ORM mappers on Base.metadata


def _async_database_url() -> str:
    url = settings.database_url.strip()
    if url.startswith("postgresql+asyncpg://"):
        return url
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url

def _sync_database_url() -> str:
    url = settings.database_url.strip()
    if "+asyncpg" in url:
        return url.replace("+asyncpg", "+psycopg", 1)
    return url


# Sync Engine & Session
engine = create_engine(_sync_database_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Async Engine & Session
async_engine = create_async_engine(
    _async_database_url(),
    echo=settings.environment == "dev",
)
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def dispose_async_engine() -> None:
    await async_engine.dispose()
