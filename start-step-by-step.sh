#!/bin/bash

echo "🚀 Поэтапный запуск Social Rent App"
echo "=================================="

# Проверка конфигурации
echo "🔧 Проверка конфигурации..."
./test-config.sh
if [ $? -ne 0 ]; then
    echo "❌ Ошибка в конфигурации. Исправьте и попробуйте снова."
    exit 1
fi

echo ""
echo "🛑 Остановка существующих контейнеров..."
docker-compose -f docker-compose.server.yml down 2>/dev/null

echo ""
echo "📦 Шаг 1: Запуск базы данных..."
docker-compose -f docker-compose.server.yml --env-file .env up -d db

echo "⏳ Ожидание готовности базы данных (60 секунд)..."
sleep 60

echo "🔍 Проверка статуса базы данных..."
if docker exec social_rent_db pg_isready -U postgres -d social_rent; then
    echo "✅ База данных готова"
else
    echo "❌ База данных не готова. Проверьте логи:"
    docker-compose -f docker-compose.server.yml logs db
    exit 1
fi

echo ""
echo "📦 Шаг 2: Запуск backend..."
docker-compose -f docker-compose.server.yml --env-file .env up -d backend

echo "⏳ Ожидание запуска backend (45 секунд)..."
sleep 45

echo "🔍 Проверка backend..."
echo "Статус контейнера:"
docker-compose -f docker-compose.server.yml ps backend

echo ""
echo "Логи backend (последние 20 строк):"
docker-compose -f docker-compose.server.yml logs --tail=20 backend

echo ""
echo "Проверка health endpoint:"
if curl -f http://localhost:8001/health 2>/dev/null; then
    echo "✅ Backend работает корректно"
else
    echo "⚠️  Backend не отвечает на HTTP запросы (возможно, еще загружается)"
fi

echo ""
echo "📦 Шаг 3: Запуск Telegram бота..."
docker-compose -f docker-compose.server.yml --env-file .env up -d bot

echo "⏳ Ожидание запуска бота (15 секунд)..."
sleep 15

echo ""
echo "📊 Финальный статус всех сервисов:"
docker-compose -f docker-compose.server.yml ps

echo ""
echo "🔗 Проверьте доступность сервисов:"
echo "   Backend API: http://185.36.141.151:8001/health"
echo "   API Docs: http://185.36.141.151:8001/docs"
echo "   База данных: порт 5435"

echo ""
echo "📝 Для просмотра логов используйте:"
echo "   docker-compose -f docker-compose.server.yml logs -f [service_name]"

echo ""
echo "🎉 Поэтапный запуск завершен!"