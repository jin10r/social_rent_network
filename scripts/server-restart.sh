#!/bin/bash

echo "🔄 Перезапуск сервисов на сервере..."

if [ ! -f "docker-compose.server.yml" ]; then
    echo "❌ Файл docker-compose.server.yml не найден!"
    exit 1
fi

if [ ! -f ".env" ]; then
    echo "❌ Файл .env не найден!"
    exit 1
fi

echo "🛑 Остановка сервисов..."
docker-compose -f docker-compose.server.yml down

echo "🚀 Запуск сервисов..."
docker-compose -f docker-compose.server.yml --env-file .env up -d

echo "⏳ Ожидание запуска..."
sleep 15

echo "📊 Статус сервисов:"
docker-compose -f docker-compose.server.yml ps

echo "✅ Перезапуск завершен!"