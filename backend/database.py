import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DEFAULT_DATABASE_URL = "postgresql+asyncpg://postgres:pg-auth@127.0.0.1:5432/postgres"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
RESET_DB = os.getenv("RESET_DB", "false").lower() in {"1", "true", "yes"}
ALLOW_RESET_DB = os.getenv("ALLOW_RESET_DB", "false").lower() in {"1", "true", "yes"}
AUTO_CREATE_TABLES = os.getenv("AUTO_CREATE_TABLES", "true").lower() in {"1", "true", "yes"}
SQL_ECHO = os.getenv("SQL_ECHO", "false").lower() in {"1", "true", "yes"}
primary_engine = create_async_engine(DATABASE_URL, echo=SQL_ECHO, future=True, pool_pre_ping=True)
Base = declarative_base()
async_session_factory = sessionmaker(bind=primary_engine, class_=AsyncSession, expire_on_commit=False)


async def setup_db():
    if RESET_DB and not ALLOW_RESET_DB:
        raise RuntimeError("RESET_DB=true 需要同时设置 ALLOW_RESET_DB=true 才能执行")
    if not AUTO_CREATE_TABLES and not RESET_DB:
        return
    async with primary_engine.begin() as conn:
        if RESET_DB:
            await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with async_session_factory() as session:
        yield session
