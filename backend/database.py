from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
from models import Base
import os
import asyncio
from typing import AsyncGenerator
import logging

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres123@localhost:5433/social_rent")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    future=True,
)

# Create async session maker
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_database() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def check_database_health():
    """Check if database is ready and accessible"""
    max_retries = 30
    retry_interval = 2
    
    for attempt in range(max_retries):
        try:
            async with engine.begin() as conn:
                # Simple query to check connectivity
                result = await conn.execute(text("SELECT 1"))
                logging.info("Database health check passed")
                return True
        except Exception as e:
            logging.warning(f"Database health check attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_interval)
            else:
                logging.error("Database health check failed after all attempts")
                raise e

async def init_database():
    """Initialize database tables"""
    # Wait for database to be ready
    await check_database_health()
    
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        logging.info("Database tables created successfully")