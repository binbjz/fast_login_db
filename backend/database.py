from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://postgres:pg-auth@10.211.55.5:5432/postgres"
primary_engine = create_async_engine(DATABASE_URL, echo=True, future=True)
Base = declarative_base()


async def setup_db():
    async with primary_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async_session = sessionmaker(bind=primary_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session

