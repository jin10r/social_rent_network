"""
Простой тест аутентификации без базы данных
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import logging
import json

# Импорт новой системы аутентификации
from auth_new import verify_telegram_auth_secure

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Auth Test API",
    description="Simple auth test without database",
    version="1.0.0"
)

# CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Auth Test API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "auth_test"}

@app.get("/api/test-auth")
async def test_auth(
    current_user_data: dict = Depends(verify_telegram_auth_secure)
):
    """Тестовый endpoint для проверки аутентификации"""
    return {
        "message": "🎉 Authentication successful!",
        "user_data": current_user_data,
        "telegram_id": current_user_data.get('id'),
        "first_name": current_user_data.get('first_name'),
        "username": current_user_data.get('username'),
        "timestamp": current_user_data.get('auth_date'),
        "is_mock_data": current_user_data.get('id') == 123456789
    }

@app.get("/api/users/me/secure")
async def mock_get_profile(
    current_user_data: dict = Depends(verify_telegram_auth_secure)
):
    """Мок endpoint для получения профиля"""
    return {
        "id": f"user_{current_user_data.get('id')}",
        "telegram_id": current_user_data.get('id'),
        "username": current_user_data.get('username'),
        "first_name": current_user_data.get('first_name'),
        "last_name": current_user_data.get('last_name'),
        "photo_url": current_user_data.get('photo_url'),
        "age": None,
        "bio": None,
        "price_min": None,
        "price_max": None,
        "metro_station": None,
        "search_radius": 1000,
        "is_active": True,
        "created_at": "2025-08-07T17:00:00Z",
        "updated_at": "2025-08-07T17:00:00Z",
        "is_new_user": True
    }

@app.put("/api/users/profile/secure")
async def mock_update_profile(
    user_data: dict,
    current_user_data: dict = Depends(verify_telegram_auth_secure)
):
    """Мок endpoint для обновления профиля"""
    logger.info(f"Mock profile update for telegram_id: {current_user_data.get('id')}")
    logger.info(f"Update data: {user_data}")
    
    # Возвращаем обновленные данные
    return {
        "id": f"user_{current_user_data.get('id')}",
        "telegram_id": current_user_data.get('id'),
        "username": current_user_data.get('username'),
        "first_name": user_data.get('first_name', current_user_data.get('first_name')),
        "last_name": user_data.get('last_name', current_user_data.get('last_name')),
        "photo_url": current_user_data.get('photo_url'),
        "age": user_data.get('age'),
        "bio": user_data.get('bio'),
        "price_min": user_data.get('price_min'),
        "price_max": user_data.get('price_max'),
        "metro_station": user_data.get('metro_station'),
        "search_radius": user_data.get('search_radius', 1000),
        "is_active": True,
        "created_at": "2025-08-07T17:00:00Z",
        "updated_at": "2025-08-07T17:35:00Z",
        "profile_updated": True,
        "update_data_received": user_data
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")