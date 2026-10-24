import logging
import os
from collections.abc import AsyncIterator

from dotenv import load_dotenv
from fastapi import HTTPException, status
from sqlalchemy import URL
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

load_dotenv()

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


engine: AsyncEngine | None = None
async_session_maker: async_sessionmaker[AsyncSession] | None = None


def _database_url() -> URL:
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    name = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")

    if not host or not port or not name or not user or password is None:
        raise ValueError("Database configuration is incomplete")

    return URL.create(
        "postgresql+asyncpg",
        username=user,
        password=password,
        host=host,
        port=int(port),
        database=name,
    )


async def initialize_database() -> None:
    global engine, async_session_maker

    candidate_engine: AsyncEngine | None = None
    try:
        from app.models.charge_model import Charge

        candidate_engine = create_async_engine(_database_url())
        async with candidate_engine.begin() as connection:
            await connection.run_sync(Charge.metadata.create_all)
    except (SQLAlchemyError, ValueError):
        logger.exception("Database connection failed")
        if candidate_engine is not None:
            await candidate_engine.dispose()
        return

    engine = candidate_engine
    async_session_maker = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )
    logger.info("Database connection established")


async def get_db_session() -> AsyncIterator[AsyncSession]:
    session_maker = async_session_maker
    if session_maker is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is unavailable",
        )

    async with session_maker() as session:
        yield session
