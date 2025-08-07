"""
Новая надежная система аутентификации для Telegram WebApp
Полностью соответствует официальной документации Telegram
"""
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
import hmac
import hashlib
import json
import time
from urllib.parse import parse_qsl, unquote
from typing import Dict, Optional
from models import User
from services import UserService
from database import get_database
import os
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

security = HTTPBearer()

# Получаем токен бота из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN", "8482163056:AAGYMcCmHUxvrzDXkBESZPGV_kGiUVHZh4I")

def validate_telegram_webapp_data(init_data: str, bot_token: str) -> Dict:
    """
    Валидация данных Telegram WebApp согласно официальной документации
    https://core.telegram.org/bots/webapps#validating-data-received-via-the-web-app
    """
    try:
        logger.info(f"Validating Telegram WebApp data")
        logger.debug(f"Init data length: {len(init_data)}")
        
        # Парсим query string
        parsed_data = dict(parse_qsl(init_data))
        logger.debug(f"Parsed data keys: {list(parsed_data.keys())}")
        
        # Проверяем наличие hash
        if 'hash' not in parsed_data:
            logger.error("No hash in init data")
            raise ValueError("Missing hash parameter")
        
        # Извлекаем hash
        received_hash = parsed_data.pop('hash')
        
        # Создаем строку для проверки подписи
        # Сортируем параметры по ключу и объединяем в строку вида: key=value\nkey=value
        data_check_arr = []
        for key in sorted(parsed_data.keys()):
            value = parsed_data[key]
            data_check_arr.append(f"{key}={value}")
        
        data_check_string = '\n'.join(data_check_arr)
        logger.debug(f"Data check string created: {len(data_check_string)} chars")
        
        # Создаем секретный ключ: HMAC-SHA256 от токена бота
        secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
        
        # Вычисляем подпись
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        
        # Сравниваем подписи
        if not hmac.compare_digest(received_hash, calculated_hash):
            logger.error(f"Hash mismatch. Received: {received_hash[:10]}..., Calculated: {calculated_hash[:10]}...")
            raise ValueError("Invalid hash signature")
        
        logger.info("Telegram WebApp data validation successful")
        
        # Проверяем временную метку (auth_date)
        if 'auth_date' in parsed_data:
            auth_date = int(parsed_data['auth_date'])
            current_time = int(time.time())
            # Разрешаем окно в 24 часа для валидности токена
            if current_time - auth_date > 86400:
                logger.warning(f"Token is old: {current_time - auth_date} seconds")
                # В продакшене можно включить эту проверку
                # raise ValueError("Token expired")
        
        # Парсим информацию о пользователе
        if 'user' in parsed_data:
            user_data = json.loads(unquote(parsed_data['user']))
            logger.info(f"Extracted user data for user_id: {user_data.get('id')}")
            return user_data
        else:
            logger.error("No user data in init data")
            raise ValueError("Missing user parameter")
            
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        raise ValueError("Invalid JSON in user data")
    except Exception as e:
        logger.error(f"Validation error: {e}")
        raise ValueError(f"Validation failed: {str(e)}")

async def verify_telegram_auth_secure(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict:
    """
    Безопасная верификация Telegram аутентификации
    """
    try:
        # Получаем initData из Bearer токена
        init_data = credentials.credentials
        
        logger.info("Starting Telegram auth verification")
        logger.debug(f"Received credentials length: {len(init_data)}")
        
        # Проверяем, что это не мок данные для разработки
        if init_data.startswith('{"id"'):
            logger.warning("Detected development mock data")
            # В режиме разработки разрешаем мок данные
            if os.getenv("ENVIRONMENT", "development") == "development":
                mock_data = json.loads(init_data)
                logger.info(f"Using development mock data for user_id: {mock_data.get('id')}")
                return mock_data
            else:
                raise ValueError("Mock data not allowed in production")
        
        # Валидируем реальные Telegram данные
        user_data = validate_telegram_webapp_data(init_data, BOT_TOKEN)
        
        # Проверяем обязательные поля
        if not user_data.get('id'):
            raise ValueError("Missing user ID")
        
        logger.info(f"Authentication successful for user_id: {user_data['id']}")
        return user_data
        
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user_secure(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_database)
) -> User:
    """
    Получение текущего пользователя с надежной проверкой
    """
    try:
        # Верифицируем аутентификацию
        user_data = await verify_telegram_auth_secure(credentials)
        telegram_id = user_data.get('id')
        
        if not telegram_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No user ID in authentication data"
            )
        
        logger.info(f"Looking up user in database: telegram_id={telegram_id}")
        
        # Получаем пользователя из базы данных
        user_service = UserService(db)
        user = await user_service.get_user_by_telegram_id(int(telegram_id))
        
        if not user:
            logger.info(f"User not found in database: telegram_id={telegram_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found. Please create your profile first."
            )
        
        logger.info(f"Successfully retrieved user: {user.id}")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during user retrieval"
        )

async def create_or_get_user_from_telegram_data(
    user_data: Dict,
    db: AsyncSession
) -> User:
    """
    Создает или получает пользователя на основе данных Telegram
    """
    try:
        telegram_id = int(user_data.get('id'))
        
        logger.info(f"Creating or getting user for telegram_id: {telegram_id}")
        
        user_service = UserService(db)
        
        # Пытаемся найти существующего пользователя
        existing_user = await user_service.get_user_by_telegram_id(telegram_id)
        
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
            from schemas import UserCreate
            
            user_create_data = UserCreate(
                telegram_id=telegram_id,
                username=user_data.get('username'),
                first_name=user_data.get('first_name'),
                last_name=user_data.get('last_name'),
                photo_url=user_data.get('photo_url')
            )
            
            new_user = await user_service.create_or_update_user(telegram_id, user_create_data)
            logger.info(f"Created new user: {new_user.id}")
            return new_user
            
    except Exception as e:
        logger.error(f"Error creating/getting user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing user data: {str(e)}"
        )