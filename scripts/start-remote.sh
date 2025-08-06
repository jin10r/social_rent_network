#!/bin/bash

# ==========================================
# СКРИПТ ЗАПУСКА УДАЛЕННОГО СЕРВЕРА
# ==========================================
# Запускает: база данных + backend + bot

set -e

echo "🚀 Запуск Social Rent App - Удаленный сервер"
echo "============================================="

# Проверка наличия .env файла
if [ ! -f .env ]; then
    echo "❌ Файл .env не найден!"
    echo "Запустите: ./scripts/setup-config.sh"
    exit 1
fi

echo "📋 Проверка конфигурации..."
source .env

required_vars=("BOT_TOKEN" "DATABASE_URL_INTERNAL" "BACKEND_PORT")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Переменная $var не задана в .env файле"
        exit 1
    fi
done

echo "✅ Конфигурация проверена"

# Остановка существующих сервисов
echo "🛑 Остановка существующих сервисов..."
docker-compose -f docker-compose.remote.yml down 2>/dev/null || true

# Пересборка образов если нужно
if [ "$1" = "--build" ]; then
    echo "🔨 Пересборка образов..."
    docker-compose -f docker-compose.remote.yml build
fi

# Запуск сервисов
echo "🚀 Запуск сервисов..."
docker-compose -f docker-compose.remote.yml --env-file .env up -d

# Ожидание готовности сервисов
echo "⏳ Ожидание готовности сервисов..."
sleep 10

# Проверка статуса
echo "📊 Проверка статуса сервисов:"
docker-compose -f docker-compose.remote.yml ps

# Проверка health checks
echo
echo "🏥 Проверка health checks:"

# Проверка базы данных
if docker-compose -f docker-compose.remote.yml exec -T db pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB} >/dev/null 2>&1; then
    echo "✅ База данных готова"
else
    echo "❌ База данных не готова"
fi

# Проверка backend
sleep 5
if curl -f http://localhost:${BACKEND_PORT}/health >/dev/null 2>&1; then
    echo "✅ Backend готов"
else
    echo "❌ Backend не готов"
fi

echo
echo "🎉 Удаленный сервер запущен!"
echo
echo "📝 Полезные команды:"
echo "  docker-compose -f docker-compose.remote.yml logs -f     # Просмотр логов"
echo "  docker-compose -f docker-compose.remote.yml ps         # Статус сервисов"
echo "  docker-compose -f docker-compose.remote.yml down       # Остановка"
echo
echo "🌐 Доступные эндпоинты:"
echo "  Backend API: http://localhost:${BACKEND_PORT}"
echo "  Backend Health: http://localhost:${BACKEND_PORT}/health"
echo "  Database: localhost:${DB_EXTERNAL_PORT}"