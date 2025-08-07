"""
Простой тестовый сервер для проверки аутентификации
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import asyncio
from contextlib import asynccontextmanager

# Импорты для тестирования
from auth_new import verify_telegram_auth_secure, create_or_get_user_from_telegram_data
from database_simple import get_database, init_database
from schemas import UserUpdate, UserResponse
from models_simple import User
import json

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация приложения
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing test database...")
    await init_database()
    logger.info("Test server started")
    yield
    # Shutdown
    logger.info("Test server shutdown")

app = FastAPI(
    title="Social Rent Test API",
    description="Test API for Telegram WebApp authentication",
    version="1.0.0",
    lifespan=lifespan
)

# CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене ограничить
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Social Rent Test API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "test_api"}

# Тестовый endpoint для проверки аутентификации
@app.get("/api/test-auth")
async def test_auth(
    current_user_data: dict = Depends(verify_telegram_auth_secure)
):
    """Тестовый endpoint для проверки аутентификации"""
    return {
        "message": "Authentication successful!",
        "user_data": current_user_data,
        "telegram_id": current_user_data.get('id'),
        "first_name": current_user_data.get('first_name'),
        "username": current_user_data.get('username')
    }

# Безопасное получение профиля пользователя  
@app.get("/api/users/me/secure", response_model=dict)
async def get_current_user_profile_secure_endpoint(
    current_user_data: dict = Depends(verify_telegram_auth_secure),
    db: AsyncSession = Depends(get_database)
):
    """Безопасное получение текущего профиля пользователя"""
    try:
        logger.info(f"Getting profile for telegram_id: {current_user_data.get('id')}")
        
        # Создаем/получаем пользователя если его нет
        user = await create_or_get_user_from_telegram_data_simple(current_user_data, db)
        
        logger.info(f"Successfully retrieved user profile: {user.id}")
        
        # Возвращаем как словарь для простоты
        return {
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
        
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user profile: {str(e)}"
        )

# Безопасное обновление профиля
@app.put("/api/users/profile/secure", response_model=dict)
async def update_user_profile_secure_endpoint(
    user_data: dict,  # Принимаем как dict для простоты тестирования
    current_user_data: dict = Depends(verify_telegram_auth_secure),
    db: AsyncSession = Depends(get_database)
):
    """Безопасное обновление профиля пользователя"""
    try:
        logger.info(f"Secure profile update for telegram_id: {current_user_data.get('id')}")
        logger.info(f"Update data: {user_data}")
        
        # Сначала создаем/получаем базового пользователя из Telegram данных
        base_user = await create_or_get_user_from_telegram_data_simple(current_user_data, db)
        
        # Обновляем поля профиля
        for field, value in user_data.items():
            if hasattr(base_user, field) and value is not None:
                setattr(base_user, field, value)
                logger.debug(f"Updated field {field} = {value}")
        
        # Обновляем координаты для станции метро (мок данные для тестирования)
        if user_data.get('metro_station'):
            # Для тестирования используем мок координаты Москвы
            base_user.search_lat = 55.7558  # Центр Москвы
            base_user.search_lon = 37.6176
            logger.info(f"Updated location to: {user_data.get('metro_station')}")
        
        # Сохраняем изменения
        await db.commit()
        await db.refresh(base_user)
        
        logger.info(f"Successfully updated user profile: {base_user.id}")
        
        # Возвращаем обновленные данные
        return {
            "id": base_user.id,
            "telegram_id": base_user.telegram_id,
            "username": base_user.username,
            "first_name": base_user.first_name,
            "last_name": base_user.last_name,
            "photo_url": base_user.photo_url,
            "age": base_user.age,
            "bio": base_user.bio,
            "price_min": base_user.price_min,
            "price_max": base_user.price_max,
            "metro_station": base_user.metro_station,
            "search_radius": base_user.search_radius,
            "is_active": base_user.is_active,
            "created_at": base_user.created_at.isoformat() if base_user.created_at else None,
            "updated_at": base_user.updated_at.isoformat() if base_user.updated_at else None
        }
        
    except Exception as e:
        logger.error(f"Error in secure profile update: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user profile: {str(e)}"
        )

async def create_or_get_user_from_telegram_data_simple(
    user_data: dict,
    db: AsyncSession
) -> User:
    """
    Создает или получает пользователя на основе данных Telegram (упрощенная версия)
    """
    try:
        telegram_id = int(user_data.get('id'))
        
        logger.info(f"Creating or getting user for telegram_id: {telegram_id}")
        
        # Пытаемся найти существующего пользователя
        from sqlalchemy import select
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await db.execute(stmt)
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            logger.info(f"Found existing user: {existing_user.id}")
            # Обновляем базовую информацию из Telegram
            existing_user.username = user_data.get('username')
            existing_user.first_name = user_data.get('first_name')
            existing_user.last_name = user_data.get('last_name')
            existing_user.photo_url = user_data.get('photo_url')
            
            await db.commit()
            await db.refresh(existing_user)
            return existing_user
        else:
            logger.info(f"Creating new user for telegram_id: {telegram_id}")
            # Создаем нового пользователя с базовой информацией из Telegram
            new_user = User(
                telegram_id=telegram_id,
                username=user_data.get('username'),
                first_name=user_data.get('first_name'),
                last_name=user_data.get('last_name'),
                photo_url=user_data.get('photo_url'),
                search_radius=1000  # Значение по умолчанию
            )
            
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            
            logger.info(f"Created new user: {new_user.id}")
            return new_user
            
    except Exception as e:
        logger.error(f"Error creating/getting user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing user data: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")