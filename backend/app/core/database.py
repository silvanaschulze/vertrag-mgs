"""Database configuration and utilities."""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    """Base class for all ORM models."""


engine: AsyncEngine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    future=True,
    echo=False,
)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncIterator[AsyncSession]:
    """Yield a database session for FastAPI dependencies."""

    async with SessionLocal() as session:  # pragma: no cover - thin wrapper
        yield session