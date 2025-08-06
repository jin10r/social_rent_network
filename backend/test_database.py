from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, CheckConstraint, DECIMAL, BigInteger
from sqlalchemy.sql import func
import uuid
import os
import asyncio
from typing import AsyncGenerator
import logging

# Use SQLite for testing
DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Simple Base without Geography support
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    photo_url = Column(Text, nullable=True)
    age = Column(Integer, CheckConstraint('age >= 18 AND age <= 100'), nullable=True)
    bio = Column(Text, nullable=True)
    price_min = Column(Integer, CheckConstraint('price_min >= 0'), nullable=True)
    price_max = Column(Integer, CheckConstraint('price_max >= price_min'), nullable=True)
    metro_station = Column(String(255), nullable=True)
    # Simplified location as lat,lon text for testing
    search_location = Column(String(50), nullable=True)  # "lat,lon" format
    search_radius = Column(Integer, CheckConstraint('search_radius > 0'), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

class Listing(Base):
    __tablename__ = "listings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Integer, CheckConstraint('price >= 0'), nullable=False)
    address = Column(String(500), nullable=True)
    # Simplified location as lat,lon text for testing
    location = Column(String(50), nullable=False)  # "lat,lon" format
    rooms = Column(Integer, CheckConstraint('rooms > 0'), nullable=True)
    area = Column(DECIMAL(7, 2), CheckConstraint('area > 0'), nullable=True)
    floor = Column(Integer, nullable=True)
    total_floors = Column(Integer, nullable=True)
    metro_station = Column(String(255), nullable=True)
    metro_distance = Column(Integer, nullable=True)
    # Simplified photos as comma-separated text
    photos = Column(Text, nullable=True)  # comma-separated URLs
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

class UserLike(Base):
    __tablename__ = "user_likes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    liker_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    liked_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())

class UserMatch(Base):
    __tablename__ = "user_matches"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user1_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user2_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

class ListingLike(Base):
    __tablename__ = "listing_likes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    listing_id = Column(String, ForeignKey("listings.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())

# Create async engine for SQLite
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
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

async def init_test_database():
    """Initialize test database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logging.info("Test database tables created successfully")

async def create_test_data():
    """Create test data for the application"""
    async with async_session_maker() as session:
        try:
            # Create test users
            users_data = [
                {
                    "id": str(uuid.uuid4()),
                    "telegram_id": 123456789,
                    "first_name": "Иван",
                    "last_name": "Петров",
                    "age": 25,
                    "bio": "Ищу квартиру в центре города",
                    "price_min": 30000,
                    "price_max": 50000,
                    "metro_station": "Тверская",
                    "search_location": "55.761,37.615",  # Moscow center
                    "search_radius": 1000
                },
                {
                    "id": str(uuid.uuid4()),
                    "telegram_id": 987654321,
                    "first_name": "Анна",
                    "last_name": "Сидорова", 
                    "age": 23,
                    "bio": "Хочу найти соседку для съема квартиры",
                    "price_min": 25000,
                    "price_max": 40000,
                    "metro_station": "Маяковская",
                    "search_location": "55.770,37.596",
                    "search_radius": 800
                }
            ]
            
            test_users = []
            for user_data in users_data:
                user = User(**user_data)
                session.add(user)
                test_users.append(user)
            
            # Create test listings
            listings_data = [
                {
                    "id": str(uuid.uuid4()),
                    "title": "Уютная 2-комнатная квартира в центре",
                    "description": "Светлая квартира рядом с метро",
                    "price": 35000,
                    "address": "ул. Тверская, 15",
                    "location": "55.761,37.615",
                    "rooms": 2,
                    "area": 65.5,
                    "floor": 3,
                    "total_floors": 9,
                    "metro_station": "Тверская",
                    "metro_distance": 300
                },
                {
                    "id": str(uuid.uuid4()),
                    "title": "1-комнатная студия у метро",
                    "description": "Современная студия для одного человека",
                    "price": 28000,
                    "address": "ул. Маяковского, 8",
                    "location": "55.770,37.596", 
                    "rooms": 1,
                    "area": 35.0,
                    "floor": 5,
                    "total_floors": 16,
                    "metro_station": "Маяковская",
                    "metro_distance": 150
                }
            ]
            
            for listing_data in listings_data:
                listing = Listing(**listing_data)
                session.add(listing)
            
            await session.commit()
            logging.info("Test data created successfully")
            return test_users
            
        except Exception as e:
            await session.rollback()
            logging.error(f"Error creating test data: {e}")
            raise