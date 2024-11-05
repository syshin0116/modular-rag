from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.configs.settings import settings
from app.db.model_base import Base

# 비동기 SQLAlchemy Engine 설정
engine = create_async_engine(settings.DATABASE_URL, echo=True)

# 비동기 SQLAlchemy Session 설정
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
