"""
Базовый FastAPI сервер без CORS для тестирования
"""
from fastapi import FastAPI
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Social Rent API (Basic)",
    description="Basic API for testing",
    version="1.0.0"
)

# Routes
@app.get("/")
async def root():
    return {"message": "Basic Social Rent API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "basic"}

@app.get("/api/test")
async def test_endpoint():
    """Тестовый эндпоинт для проверки ngrok"""
    return {
        "status": "working", 
        "message": "API работает!",
        "ngrok_url": "https://a231167a7f99.ngrok-free.app"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)