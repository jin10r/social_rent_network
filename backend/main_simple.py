"""
Простая версия API для работы с SQLite и ngrok
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from contextlib import asynccontextmanager
import os
import uuid
from typing import List, Optional
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Используем простые модели и базу данных
from models_simple import User, Listing, UserLike, UserMatch, ListingLike
from schemas import (
    UserCreate, UserUpdate, UserResponse,
    ListingResponse, UserProfileResponse,
    LikeUserRequest, MatchResponse
)
from database_simple import get_database, init_database, async_session_maker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Фиктивные данные для тестирования
MOCK_TELEGRAM_USER = {
    "id": 123456789,
    "first_name": "Тест",
    "last_name": "Пользователь", 
    "username": "testuser",
    "photo_url": None
}

# Initialize FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Application startup: Initializing SQLite database...")
    await init_database()
    logger.info("Application startup completed")
    yield
    # Shutdown
    logger.info("Application shutdown")

app = FastAPI(
    title="Social Rent API (Simple)",
    description="API for Telegram housing social network with SQLite",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for ngrok - temporarily disabled for debugging
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# Фиктивная аутентификация для тестирования
async def get_mock_current_user(db: AsyncSession = Depends(get_database)) -> User:
    """Создает или возвращает тестового пользователя"""
    result = await db.execute(
        select(User).where(User.telegram_id == MOCK_TELEGRAM_USER["id"])
    )
    user = result.scalar_one_or_none()
    
    if not user:
        # Создаем нового тестового пользователя
        user = User(
            telegram_id=MOCK_TELEGRAM_USER["id"],
            username=MOCK_TELEGRAM_USER["username"],
            first_name=MOCK_TELEGRAM_USER["first_name"],
            last_name=MOCK_TELEGRAM_USER["last_name"],
            photo_url=MOCK_TELEGRAM_USER["photo_url"]
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info(f"Created new mock user: {user.id}")
    
    return user

# Routes
@app.get("/")
async def root():
    return {"message": "Social Rent API (Simple) is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "SQLite"}

# Эндпоинты для профиля пользователя (совместимые с фронтендом)
@app.get("/api/users/me/secure", response_model=dict)
async def get_current_user_profile_secure(
    db: AsyncSession = Depends(get_database)
):
    """Безопасное получение текущего профиля пользователя (mock version)"""
    try:
        user = await get_mock_current_user(db)
        
        # Преобразуем в формат ответа
        user_dict = {
            "id": user.id,
            "telegram_id": user.telegram_id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "photo_url": user.photo_url,
            "age": user.age,
            "bio": user.bio,
            "price_min": user.price_min,
            "price_max": user.price_max,
            "metro_station": user.metro_station,
            "search_radius": user.search_radius,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        }
        
        logger.info(f"Successfully retrieved user profile: {user.id}")
        return user_dict
        
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user profile: {str(e)}"
        )

@app.put("/api/users/profile/secure", response_model=dict)
async def update_user_profile_secure(
    user_data: dict,
    db: AsyncSession = Depends(get_database)
):
    """Безопасное обновление профиля пользователя (mock version)"""
    try:
        logger.info(f"Updating profile with data: {user_data}")
        
        user = await get_mock_current_user(db)
        
        # Обновляем поля
        if "first_name" in user_data and user_data["first_name"]:
            user.first_name = user_data["first_name"].strip()
        if "last_name" in user_data and user_data["last_name"]:
            user.last_name = user_data["last_name"].strip()
        if "age" in user_data and user_data["age"]:
            user.age = int(user_data["age"])
        if "bio" in user_data:
            user.bio = user_data["bio"].strip() if user_data["bio"] else None
        if "price_min" in user_data and user_data["price_min"]:
            user.price_min = int(user_data["price_min"])
        if "price_max" in user_data and user_data["price_max"]:
            user.price_max = int(user_data["price_max"])
        if "metro_station" in user_data and user_data["metro_station"]:
            user.metro_station = user_data["metro_station"].strip()
        if "search_radius" in user_data and user_data["search_radius"]:
            user.search_radius = int(user_data["search_radius"])
        
        # Сохраняем изменения
        await db.commit()
        await db.refresh(user)
        
        # Возвращаем обновленного пользователя
        user_dict = {
            "id": user.id,
            "telegram_id": user.telegram_id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "photo_url": user.photo_url,
            "age": user.age,
            "bio": user.bio,
            "price_min": user.price_min,
            "price_max": user.price_max,
            "metro_station": user.metro_station,
            "search_radius": user.search_radius,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        }
        
        logger.info(f"Successfully updated user profile: {user.id}")
        return user_dict
        
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user profile: {str(e)}"
        )

# Эндпоинт для получения станций метро
@app.get("/api/metro/stations", response_model=List[str])
async def get_metro_stations():
    """Получить все станции метро"""
    # Простой список станций метро Москвы для тестирования
    stations = [
        "Сокольники", "Красносельская", "Комсомольская", "Красные ворота",
        "Чистые пруды", "Лубянка", "Охотный ряд", "Библиотека им. Ленина",
        "Кропоткинская", "Парк культуры", "Фрунзенская", "Спортивная",
        "Воробьевы горы", "Университет", "Проспект Вернадского", "Юго-Западная",
        "Тропарево", "Румянцево", "Саларьево", "Филатов Луг", "Прокшино",
        "Ольховая", "Коммунарка", "Китай-город", "Третьяковская", "Октябрьская",
        "Добрынинская", "Павелецкая", "Автозаводская", "Технопарк", "Коломенская",
        "Каширская", "Кантемировская", "Царицыно", "Орехово", "Домодедовская",
        "Красногвардейская", "Алма-Атинская"
    ]
    return stations

# Простые эндпоинты для тестирования
@app.get("/api/test")
async def test_endpoint():
    """Тестовый эндпоинт для проверки API"""
    return {
        "status": "working",
        "message": "API через ngrok работает!",
        "backend_url": os.getenv("BACKEND_URL", "не настроен"),
        "webapp_url": os.getenv("WEBAPP_URL", "не настроен")
    }

@app.get("/api/users/test", response_model=List[dict])
async def get_test_users(db: AsyncSession = Depends(get_database)):
    """Получение всех пользователей для тестирования"""
    result = await db.execute(select(User))
    users = result.scalars().all()
    
    return [
        {
            "id": user.id,
            "telegram_id": user.telegram_id,
            "username": user.username,
            "first_name": user.first_name,
            "age": user.age,
            "metro_station": user.metro_station,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
        for user in users
    ]

@app.post("/api/users/create-test")
async def create_test_user(db: AsyncSession = Depends(get_database)):
    """Создание тестового пользователя"""
    import random
    
    test_user = User(
        telegram_id=random.randint(100000, 999999),
        username=f"testuser_{random.randint(1, 1000)}",
        first_name="Тест",
        last_name="Пользователь",
        age=25,
        bio="Тестовый пользователь для проверки API",
        price_min=30000,
        price_max=60000,
        metro_station="Сокольники",
        search_lat=55.7558,
        search_lon=37.6176,
        search_radius=5000
    )
    
    db.add(test_user)
    await db.commit()
    await db.refresh(test_user)
    
    return {
        "message": "Тестовый пользователь создан",
        "user": {
            "id": test_user.id,
            "telegram_id": test_user.telegram_id,
            "username": test_user.username,
            "metro_station": test_user.metro_station
        }
    }

@app.get("/api/listings/test", response_model=List[dict])
async def get_test_listings(db: AsyncSession = Depends(get_database)):
    """Получение всех объявлений для тестирования"""
    result = await db.execute(select(Listing))
    listings = result.scalars().all()
    
    return [
        {
            "id": listing.id,
            "title": listing.title,
            "price": listing.price,
            "address": listing.address,
            "metro_station": listing.metro_station,
            "rooms": listing.rooms,
            "created_at": listing.created_at.isoformat() if listing.created_at else None
        }
        for listing in listings
    ]

@app.post("/api/listings/create-test")
async def create_test_listing(db: AsyncSession = Depends(get_database)):
    """Создание тестового объявления"""
    import random
    
    metro_stations = ["Сокольники", "Красносельская", "Комсомольская", "Красные ворота", "Чистые пруды"]
    
    test_listing = Listing(
        title=f"Квартира в аренду {random.randint(1, 100)}",
        description="Уютная квартира в хорошем районе",
        price=random.randint(40000, 80000),
        address="ул. Тестовая, д. 123",
        lat=55.7558 + random.uniform(-0.05, 0.05),
        lon=37.6176 + random.uniform(-0.05, 0.05),
        rooms=random.randint(1, 3),
        area=random.randint(40, 100),
        metro_station=random.choice(metro_stations),
        metro_distance=random.randint(300, 1500)
    )
    
    db.add(test_listing)
    await db.commit()
    await db.refresh(test_listing)
    
    return {
        "message": "Тестовое объявление создано",
        "listing": {
            "id": test_listing.id,
            "title": test_listing.title,
            "price": test_listing.price,
            "metro_station": test_listing.metro_station,
            "rooms": test_listing.rooms
        }
    }

# Эндпоинт для проверки связи с фронтендом
@app.get("/api/frontend-test")
async def frontend_test():
    """Специальный эндпоинт для тестирования связи с фронтендом"""
    return {
        "message": "Связь между фронтендом и бэкендом работает!",
        "timestamp": "2025-07-25T12:00:00Z",
        "backend_status": "healthy",
        "database_status": "SQLite connected"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)