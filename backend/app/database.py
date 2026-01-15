"""
資料庫連線設定
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


# 建立非同步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
)

# 建立非同步 Session 工廠
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """SQLAlchemy 基礎類別"""
    pass


async def get_db():
    """取得資料庫 Session（依賴注入用）"""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """初始化資料庫（建立所有表格）"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
