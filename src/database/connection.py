from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData
from typing import AsyncGenerator
import logging

from config.settings import settings

logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

# Create async engine with proper configuration
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=getattr(settings, 'DATABASE_POOL_SIZE', 10),
    max_overflow=getattr(settings, 'DATABASE_MAX_OVERFLOW', 20),
    pool_pre_ping=True,
    echo=settings.DEBUG,
    future=True  # Enable SQLAlchemy 2.0 style
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Database session dependency"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            await session.close()

async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully")

async def close_db():
    """Close database connections"""
    await engine.dispose()
    logger.info("Database connections closed")
