from contextlib import asynccontextmanager
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from src.utils.other import ENV_PATH
from src.config import settings

load_dotenv(ENV_PATH)


engine = create_async_engine(
    settings.db.url,
    echo=False,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)


async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# для Fastapi
async def get_session():
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


# для Celery
@asynccontextmanager
async def get_celery_session():
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


class Base(DeclarativeBase):
    pass
