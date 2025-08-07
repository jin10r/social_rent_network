#!/bin/bash

# =============================================================================
# SOCIAL RENT APP - STARTUP SCRIPT
# =============================================================================

set -e

echo "🚀 Запуск Social Rent App"
echo "========================="

# Проверяем наличие .env файла
if [ ! -f ".env" ]; then
    echo "❌ Файл .env не найден!"
    echo "Создайте файл .env на основе примера в README.md"
    exit 1
fi

# Проверяем, установлен ли Docker и Docker Compose
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен!"
    echo "Установите Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен!"
    echo "Установите Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# Остановка предыдущих контейнеров (если есть)
echo "🧹 Остановка предыдущих контейнеров..."
docker-compose down 2>/dev/null || true

# Сборка и запуск всех сервисов
echo "🔨 Сборка и запуск сервисов..."
docker-compose up --build -d

# Ждем, пока сервисы запустятся
echo "⏳ Ожидание запуска сервисов..."
sleep 10

# Проверка статуса сервисов
echo "📊 Статус сервисов:"
docker-compose ps

echo ""
echo "✅ Social Rent App запущен!"
echo ""
echo "📱 Доступ к приложению:"
echo "   - Локально: http://localhost"
echo "   - Через ngrok: обновите WEBAPP_URL в .env"
echo ""
echo "🛠️ Полезные команды:"
echo "   - Логи всех сервисов: docker-compose logs -f"
echo "   - Логи backend: docker-compose logs -f backend"
echo "   - Логи frontend: docker-compose logs -f frontend"
echo "   - Статус: docker-compose ps"
echo "   - Остановка: docker-compose down"
echo ""
echo "🔗 Настройте ngrok:"
echo "   1. ngrok http 80"
echo "   2. Скопируйте HTTPS URL"
echo "   3. Обновите WEBAPP_URL и REACT_APP_BACKEND_URL в .env"
echo "   4. docker-compose restart"
echo ""