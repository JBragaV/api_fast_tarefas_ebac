from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core import SysConfig

DATABASE_URL = SysConfig.DATABASE_URL
DEBUG = SysConfig.DEBUG

engine = (
    create_async_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    if DEBUG
    else create_async_engine(DATABASE_URL)
)
SessionLocal = async_sessionmaker(autoflush=False, bind=engine, class_=AsyncSession)


async def get_session():
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
