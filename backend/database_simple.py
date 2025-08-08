"""
Простая база данных для тестирования (SQLite)
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from models import Base
import os

# Для тестирования используем SQLite
DATABASE_URL = "sqlite+aiosqlite:///./social_rent_test.db"

# Создаем движок базы данных
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Показывать SQL запросы для отладки
    future=True
)

# Создаем сессию
async_session_maker = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def init_database():
    """Инициализация базы данных"""
    async with engine.begin() as conn:
        # Создаем все таблицы
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database initialized")

async def get_database() -> AsyncSession:
    """Получение сессии базы данных"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()