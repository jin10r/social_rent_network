#!/bin/bash

echo "💻 Запуск локального frontend приложения..."

# Проверка наличия .env файла
if [ ! -f ".env" ]; then
    echo "❌ Файл .env не найден!"
    echo "📝 Создайте .env файл с необходимыми настройками"
    exit 1
fi

# Проверка docker-compose файла
if [ ! -f "docker-compose.local.yml" ]; then
    echo "❌ Файл docker-compose.local.yml не найден!"
    exit 1
fi

echo "📋 Проверка конфигурации..."
BACKEND_URL=$(grep REACT_APP_BACKEND_URL .env | cut -d'=' -f2)
if [ "$BACKEND_URL" != "http://YOUR_SERVER_IP_HERE:8001" ]; then
    echo "✅ REACT_APP_BACKEND_URL настроен: $BACKEND_URL"
else
    echo "⚠️  Необходимо настроить REACT_APP_BACKEND_URL в .env файле"
fi

echo "🐳 Запуск Docker Compose для frontend..."
docker-compose -f docker-compose.local.yml --env-file .env up -d

echo "⏳ Ожидание запуска frontend..."
sleep 5

echo "📊 Статус frontend:"
docker-compose -f docker-compose.local.yml ps

echo ""
echo "🎉 Локальный frontend запущен!"
echo ""
echo "📝 Следующие шаги:"
echo "1. 🌐 Запустите ngrok в новом терминале:"
echo "     ngrok http 3000"
echo ""
echo "2. 📋 Скопируйте HTTPS URL из ngrok"
echo ""  
echo "3. ✏️  Обновите настройки в .env файле:"
echo "     WEBAPP_URL=https://your-ngrok-url.ngrok-free.app"
echo "     ALLOWED_ORIGINS=http://localhost:3000,https://your-ngrok-url.ngrok-free.app"
echo ""
echo "4. 🔄 Перезапустите серверные сервисы:"
echo "     ./scripts/server-restart.sh"
echo ""
echo "📝 Полезные команды:"
echo "   Логи:      docker-compose -f docker-compose.local.yml logs -f"
echo "   Статус:    docker-compose -f docker-compose.local.yml ps"
echo "   Остановка: docker-compose -f docker-compose.local.yml down"
echo "   Рестарт:   docker-compose -f docker-compose.local.yml restart"
echo ""
echo "🔗 Frontend доступен:"
echo "   Локально: http://localhost:3000"
echo "   Ngrok:    https://your-ngrok-url.ngrok-free.app"