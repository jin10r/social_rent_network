"""
Новые безопасные endpoints для работы с профилем пользователя
"""
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from typing import Dict

# Импортируем новую систему аутентификации
from auth_new import (
    verify_telegram_auth_secure, 
    get_current_user_secure,
    create_or_get_user_from_telegram_data
)
from database import get_database
from services import UserService
from schemas import UserUpdate, UserResponse, UserProfileResponse
from models import User

logger = logging.getLogger(__name__)

# Новые безопасные endpoints для добавления к main.py

async def create_or_update_user_secure(
    user_data: UserUpdate,
    current_user_data: dict = Depends(verify_telegram_auth_secure),
    db: AsyncSession = Depends(get_database)
) -> UserResponse:
    """
    Безопасное создание или обновление пользователя
    """
    try:
        logger.info(f"Secure user create/update for telegram_id: {current_user_data.get('id')}")
        
        # Сначала создаем/получаем базового пользователя из Telegram данных
        base_user = await create_or_get_user_from_telegram_data(current_user_data, db)
        
        # Теперь обновляем профиль пользовательскими данными
        user_service = UserService(db)
        
        # Обновляем поля профиля
        for field, value in user_data.dict(exclude_unset=True, exclude={'lat', 'lon'}).items():
            if hasattr(base_user, field) and value is not None:
                setattr(base_user, field, value)
                logger.debug(f"Updated field {field} = {value}")
        
        # Обновляем локацию если указана станция метро
        if user_data.metro_station:
            from metro_stations import get_metro_station_info
            station_info = get_metro_station_info(user_data.metro_station)
            if station_info:
                from sqlalchemy import func
                location_text = f'POINT({station_info["lon"]} {station_info["lat"]})'
                base_user.search_location = func.ST_GeogFromText(location_text)
                logger.info(f"Updated location to: {user_data.metro_station}")
            else:
                logger.warning(f"Metro station not found: {user_data.metro_station}")
        elif user_data.lat is not None and user_data.lon is not None:
            from sqlalchemy import func
            location_text = f'POINT({user_data.lon} {user_data.lat})'
            base_user.search_location = func.ST_GeogFromText(location_text)
            logger.info(f"Updated location to coordinates: {user_data.lat}, {user_data.lon}")
        
        # Сохраняем изменения
        await db.commit()
        await db.refresh(base_user)
        
        logger.info(f"Successfully updated user profile: {base_user.id}")
        
        return base_user
        
    except Exception as e:
        logger.error(f"Error in secure user create/update: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save user profile: {str(e)}"
        )

async def get_current_user_profile_secure(
    current_user_data: dict = Depends(verify_telegram_auth_secure),
    db: AsyncSession = Depends(get_database)
) -> UserResponse:
    """
    Безопасное получение текущего профиля пользователя
    """
    try:
        logger.info(f"Getting profile for telegram_id: {current_user_data.get('id')}")
        
        # Создаем/получаем пользователя если его нет
        user = await create_or_get_user_from_telegram_data(current_user_data, db)
        
        logger.info(f"Successfully retrieved user profile: {user.id}")
        return user
        
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user profile: {str(e)}"
        )

# Добавить эти endpoints в main.py:

"""
# Безопасные endpoints для профиля пользователя
@app.post("/api/users/secure", response_model=UserResponse)
async def create_or_update_user_secure_endpoint(
    user_data: UserUpdate,
    current_user_data: dict = Depends(verify_telegram_auth_secure),
    db: AsyncSession = Depends(get_database)
):
    \"\"\"Безопасное создание или обновление пользователя\"\"\"
    return await create_or_update_user_secure(user_data, current_user_data, db)

@app.get("/api/users/me/secure", response_model=UserResponse)
async def get_current_user_profile_secure_endpoint(
    current_user_data: dict = Depends(verify_telegram_auth_secure),
    db: AsyncSession = Depends(get_database)
):
    \"\"\"Безопасное получение текущего профиля пользователя\"\"\"
    return await get_current_user_profile_secure(current_user_data, db)

@app.put("/api/users/profile/secure", response_model=UserResponse)
async def update_user_profile_secure_endpoint(
    user_data: UserUpdate,
    current_user_data: dict = Depends(verify_telegram_auth_secure),
    db: AsyncSession = Depends(get_database)
):
    \"\"\"Безопасное обновление профиля пользователя\"\"\"
    return await create_or_update_user_secure(user_data, current_user_data, db)
"""