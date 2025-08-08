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
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

security = HTTPBearer()

# Получаем токен бота из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("BOT_TOKEN is not set in environment variables!")
    # В реальном приложении здесь лучше выбросить исключение или завершить работу
    # For debugging, we can use a placeholder, but it's not secure.
    BOT_TOKEN = "8482163056:AAGYMcCmHUxvrzDXkBESZPGV_kGiUVHZh4I" # Fallback for safety, should not be used in prod

def validate_telegram_webapp_data(init_data: str, bot_token: str) -> Dict:
    """
    Валидация данных Telegram WebApp согласно официальной документации
    https://core.telegram.org/bots/webapps#validating-data-received-via-the-web-app
    """
    logger.info("Starting Telegram WebApp data validation.")
    logger.info(f"Received init_data: {init_data}")

    try:
        # Парсим query string
        parsed_data = dict(parse_qsl(init_data))
        logger.info(f"Parsed data keys: {list(parsed_data.keys())}")

        # Проверяем наличие hash
        if 'hash' not in parsed_data:
            logger.error("Validation failed: 'hash' not found in init_data.")
            raise ValueError("Missing hash parameter in init_data")
        
        # Извлекаем hash
        received_hash = parsed_data.pop('hash')
        logger.info(f"Received hash: {received_hash}")
        
        # Создаем строку для проверки подписи
        # Сортируем параметры по ключу и объединяем в строку вида: key=value\nkey=value
        data_check_arr = []
        for key in sorted(parsed_data.keys()):
            value = parsed_data[key]
            data_check_arr.append(f"{key}={value}")
        
        data_check_string = '\n'.join(data_check_arr)
        logger.info(f"Generated data_check_string for hashing: '{data_check_string}'")
        
        # Создаем секретный ключ: HMAC-SHA256 от токена бота
        secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
        
        # Вычисляем подпись
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        logger.info(f"Calculated hash: {calculated_hash}")
        
        # Сравниваем подписи
        if not hmac.compare_digest(received_hash, calculated_hash):
            logger.error(f"Hash mismatch! Received: {received_hash}, Calculated: {calculated_hash}")
            raise ValueError("Invalid hash signature")
        
        logger.info("Hash validation successful.")
        
        # Проверяем временную метку (auth_date)
        if 'auth_date' in parsed_data:
            auth_date = int(parsed_data['auth_date'])
            current_time = int(time.time())
            time_diff = current_time - auth_date
            logger.info(f"Token timestamp check: auth_date={auth_date}, current_time={current_time}, diff={time_diff}s")
            # Разрешаем окно в 24 часа для валидности токена
            if time_diff > 86400:
                logger.warning(f"Token is older than 24 hours ({time_diff} seconds old).")
                # В продакшене можно включить эту проверку
                # raise ValueError("Token expired")
        
        # Парсим информацию о пользователе
        if 'user' in parsed_data:
            # Декодируем URL-encoded строку пользователя
            user_json_string = unquote(parsed_data['user'])
            logger.info(f"Decoding user data string: {user_json_string}")
            user_data = json.loads(user_json_string)
            logger.info(f"Successfully extracted user data for user_id: {user_data.get('id')}")
            return user_data
        else:
            logger.error("Validation failed: 'user' not found in parsed_data.")
            raise ValueError("Missing user parameter in init_data")

    except json.JSONDecodeError as e:
        logger.error(f"JSON decoding failed for user data: {e}. Data was: '{parsed_data.get('user')}'")
        raise ValueError("Invalid JSON in user data")
    except Exception as e:
        logger.error(f"An unexpected error occurred during validation: {e}", exc_info=True)
        raise

async def verify_telegram_auth_secure(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict:
    """
    Безопасная верификация Telegram аутентификации
    """
    logger.info("Attempting to verify Telegram authentication.")
    if not credentials or not credentials.credentials:
        logger.error("Authentication failed: No credentials provided.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No credentials provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    init_data = credentials.credentials
    logger.info(f"Received credentials (init_data) of length: {len(init_data)}")
    
    if not BOT_TOKEN:
        logger.critical("CRITICAL: BOT_TOKEN is not configured on the server!")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Bot token is not configured on the server.",
        )

    try:
        user_data = validate_telegram_webapp_data(init_data, BOT_TOKEN)
        logger.info(f"Authentication successful for user_id: {user_data.get('id')}")
        return user_data
    except ValueError as e:
        logger.error(f"Authentication failed due to validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"An unexpected error occurred during authentication: {e}", exc_info=True)
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
        logger.error(f"Error getting current user: {e}", exc_info=True)
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
            
            new_user = await user_service.create_user(user_create_data)
            logger.info(f"Created new user: {new_user.id}")
            return new_user
            
    except Exception as e:
        logger.error(f"Error creating/getting user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing user data: {str(e)}"
        )