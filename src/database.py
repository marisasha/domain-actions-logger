import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from src.utils import ENV_PATH

load_dotenv(ENV_PATH)

DATABASE_URL = os.getenv("DATABASE_URL")


engine = create_async_engine(
    DATABASE_URL,
    echo=True,
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


async def get_session():
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


class Base(DeclarativeBase):
    pass
