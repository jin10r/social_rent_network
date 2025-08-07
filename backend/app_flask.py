"""
Flask API для тестирования ngrok
"""
from flask import Flask, jsonify
from flask_cors import CORS
import os

# Create Flask app
app = Flask(__name__)

# Configure CORS
CORS(app, origins="*")

@app.route('/')
def root():
    return jsonify({"message": "Flask Social Rent API is running"})

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "version": "flask"})

@app.route('/api/test')
def test_endpoint():
    """Тестовый эндпоинт для проверки ngrok"""
    return jsonify({
        "status": "working", 
        "message": "API через ngrok работает!",
        "ngrok_url": "https://a231167a7f99.ngrok-free.app",
        "backend_url": os.getenv("BACKEND_URL", "не настроен"),
        "webapp_url": os.getenv("WEBAPP_URL", "не настроен"),
        "api_prefix": "/api"
    })

@app.route('/api/frontend-test')
def frontend_test():
    """Эндпоинт для тестирования связи с фронтендом"""
    return jsonify({
        "message": "Связь между фронтендом и бэкендом через nginx работает!",
        "backend_port": "8001",
        "frontend_port": "3000", 
        "nginx_routing": "OK"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001, debug=True)