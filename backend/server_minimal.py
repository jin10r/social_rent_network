"""
Минимальный FastAPI сервер для тестирования ngrok
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Social Rent API (Minimal)",
    description="Minimal API for testing ngrok connection",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
@app.get("/")
async def root():
    return {"message": "Minimal Social Rent API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "minimal"}

@app.get("/api/test")
async def test_endpoint():
    """Тестовый эндпоинт для проверки ngrok"""
    return {
        "status": "working", 
        "message": "API через ngrok работает!",
        "ngrok_url": "https://a231167a7f99.ngrok-free.app",
        "backend_url": os.getenv("BACKEND_URL", "не настроен"),
        "webapp_url": os.getenv("WEBAPP_URL", "не настроен"),
        "api_prefix": "/api"
    }

@app.get("/api/frontend-test")
async def frontend_test():
    """Эндпоинт для тестирования связи с фронтендом"""
    return {
        "message": "Связь между фронтендом и бэкендом через nginx работает!",
        "backend_port": "8001",
        "frontend_port": "3000",
        "nginx_routing": "OK"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)