#!/bin/bash

# ==========================================
# СКРИПТ ЗАПУСКА ЛОКАЛЬНОГО ФРОНТЕНДА  
# ==========================================
# Запускает: frontend (подключается к удаленному backend)

set -e

echo "🚀 Запуск Social Rent App - Локальный фронтенд"
echo "==============================================="

# Проверка наличия .env файла
if [ ! -f .env ]; then
    echo "❌ Файл .env не найден!"
    echo "Запустите: ./scripts/setup-config.sh"
    exit 1
fi

echo "📋 Проверка конфигурации..."
source .env

required_vars=("BACKEND_URL" "WEBAPP_URL" "FRONTEND_PORT")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Переменная $var не задана в .env файле"
        exit 1
    fi
done

echo "✅ Конфигурация проверена"

# Проверка доступности backend
echo "🔍 Проверка доступности backend ($BACKEND_URL)..."
backend_host=$(echo $BACKEND_URL | sed 's|http://||' | sed 's|https://||' | cut -d: -f1)
backend_port=$(echo $BACKEND_URL | sed 's|.*:||')

if timeout 5 bash -c "</dev/tcp/$backend_host/$backend_port" 2>/dev/null; then
    echo "✅ Backend доступен"
else
    echo "⚠️  Backend недоступен, но продолжаем..."
fi

# Остановка существующих сервисов
echo "🛑 Остановка существующих сервисов..."
docker-compose -f docker-compose.frontend.yml down 2>/dev/null || true

# Пересборка образов если нужно
if [ "$1" = "--build" ]; then
    echo "🔨 Пересборка образа..."
    docker-compose -f docker-compose.frontend.yml build
fi

# Запуск фронтенда
echo "🚀 Запуск фронтенда..."
docker-compose -f docker-compose.frontend.yml --env-file .env up -d

# Ожидание готовности
echo "⏳ Ожидание готовности фронтенда..."
sleep 15

# Проверка статуса
echo "📊 Проверка статуса:"
docker-compose -f docker-compose.frontend.yml ps

# Проверка доступности фронтенда
echo
echo "🏥 Проверка доступности фронтенда:"
if curl -f http://localhost:${FRONTEND_PORT} >/dev/null 2>&1; then
    echo "✅ Фронтенд готов"
else
    echo "❌ Фронтенд не готов"
fi

echo
echo "🎉 Локальный фронтенд запущен!"
echo
echo "📝 Полезные команды:"
echo "  docker-compose -f docker-compose.frontend.yml logs -f   # Просмотр логов"
echo "  docker-compose -f docker-compose.frontend.yml down     # Остановка"
echo
echo "🌐 Доступные URL:"
echo "  Локальный фронтенд: http://localhost:${FRONTEND_PORT}"
echo "  Backend API: ${BACKEND_URL}"
echo "  Telegram Web App: ${WEBAPP_URL}"
echo
echo "💡 Настройка ngrok:"
echo "  1. ngrok http ${FRONTEND_PORT}"
echo "  2. Обновите WEBAPP_URL в .env на ngrok URL"
echo "  3. Перезапустите удаленный сервер"