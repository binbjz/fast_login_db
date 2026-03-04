import os

from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from backend.limits import USERNAME_DB_MAX_LEN

DEFAULT_DATABASE_URL = "postgresql+asyncpg://postgres:pg-auth@127.0.0.1:5432/postgres"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
RESET_DB = os.getenv("RESET_DB", "false").lower() in {"1", "true", "yes"}
ALLOW_RESET_DB = os.getenv("ALLOW_RESET_DB", "false").lower() in {"1", "true", "yes"}
AUTO_CREATE_TABLES = os.getenv("AUTO_CREATE_TABLES", "true").lower() in {"1", "true", "yes"}
SQL_ECHO = os.getenv("SQL_ECHO", "false").lower() in {"1", "true", "yes"}
primary_engine = create_async_engine(DATABASE_URL, echo=SQL_ECHO, future=True, pool_pre_ping=True)
Base = declarative_base()
async_session_factory = sessionmaker(bind=primary_engine, class_=AsyncSession, expire_on_commit=False)


def _ensure_username_column_capacity(sync_conn, allow_schema_mutation: bool) -> None:
    inspector = inspect(sync_conn)
    if "users" not in inspector.get_table_names():
        return

    username_column = next(
        (column for column in inspector.get_columns("users") if column.get("name") == "username"),
        None,
    )
    if not username_column:
        return

    current_len = getattr(username_column.get("type"), "length", None)
    if current_len is None or current_len >= USERNAME_DB_MAX_LEN:
        return

    if not allow_schema_mutation:
        raise RuntimeError(
            f"数据库 users.username 当前长度为 {current_len}，小于要求的 {USERNAME_DB_MAX_LEN}。"
            "请开启 AUTO_CREATE_TABLES 或手动执行迁移。"
        )

    if sync_conn.dialect.name != "postgresql":
        raise RuntimeError(
            f"当前数据库 {sync_conn.dialect.name} 不支持自动扩容 users.username，"
            f"请手动迁移到 VARCHAR({USERNAME_DB_MAX_LEN})。"
        )

    sync_conn.execute(
        text(f"ALTER TABLE users ALTER COLUMN username TYPE VARCHAR({USERNAME_DB_MAX_LEN})")
    )


async def setup_db():
    if RESET_DB and not ALLOW_RESET_DB:
        raise RuntimeError("RESET_DB=true 需要同时设置 ALLOW_RESET_DB=true 才能执行")
    allow_schema_mutation = AUTO_CREATE_TABLES or RESET_DB
    async with primary_engine.begin() as conn:
        if RESET_DB:
            await conn.run_sync(Base.metadata.drop_all)
        if allow_schema_mutation:
            await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_ensure_username_column_capacity, allow_schema_mutation)


async def get_db():
    async with async_session_factory() as session:
        yield session
