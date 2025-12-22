import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DEFAULT_DATABASE_URL = "postgresql+asyncpg://postgres:pg-auth@127.0.0.1:5432/postgres"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
RESET_DB = os.getenv("RESET_DB", "false").lower() in {"1", "true", "yes"}
primary_engine = create_async_engine(DATABASE_URL, echo=True, future=True)
Base = declarative_base()


async def setup_db():
    async with primary_engine.begin() as conn:
        if RESET_DB:
            await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async_session = sessionmaker(bind=primary_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
