#!/bin/bash

echo "🚀 Запуск сервисов на удаленном сервере (bot + backend + database)..."

# Проверка наличия .env файла
if [ ! -f ".env" ]; then
    echo "❌ Файл .env не найден!"
    echo "📝 Создайте .env файл с необходимыми настройками"
    echo "   Пример: cp .env.example .env && nano .env"
    exit 1
fi

# Проверка docker-compose файла
if [ ! -f "docker-compose.server.yml" ]; then
    echo "❌ Файл docker-compose.server.yml не найден!"
    exit 1
fi

echo "📋 Проверка конфигурации..."
if ! grep -q "BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_HERE" .env; then
    echo "✅ BOT_TOKEN настроен"
else
    echo "⚠️  Необходимо настроить BOT_TOKEN в .env файле"
fi

if ! grep -q "SERVER_IP=YOUR_SERVER_IP_HERE" .env; then
    echo "✅ SERVER_IP настроен"  
else
    echo "⚠️  Необходимо настроить SERVER_IP в .env файле"
fi

echo "🐳 Запуск Docker Compose..."
docker-compose -f docker-compose.server.yml --env-file .env up -d

echo "⏳ Ожидание запуска сервисов..."
sleep 10

echo "📊 Статус сервисов:"
docker-compose -f docker-compose.server.yml ps

echo ""
echo "🎉 Сервисы на сервере запущены!"
echo ""
echo "📝 Полезные команды:"
echo "   Логи:      docker-compose -f docker-compose.server.yml logs -f"
echo "   Статус:    docker-compose -f docker-compose.server.yml ps"  
echo "   Остановка: docker-compose -f docker-compose.server.yml down"
echo "   Рестарт:   docker-compose -f docker-compose.server.yml restart"
echo ""
echo "🔗 Проверьте работу:"
echo "   Backend: http://$(grep SERVER_IP .env | cut -d'=' -f2):8001/health"