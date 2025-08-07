#!/bin/bash

echo "🔧 Тестирование конфигурации docker-compose.server.yml..."

# Проверка наличия файлов
if [ ! -f ".env" ]; then
    echo "❌ Файл .env не найден!"
    exit 1
fi

if [ ! -f "docker-compose.server.yml" ]; then
    echo "❌ Файл docker-compose.server.yml не найден!"
    exit 1
fi

echo "✅ Необходимые файлы найдены"

# Загрузка переменных из .env
source .env

echo ""
echo "📋 Проверка ключевых переменных:"

# Проверка критических переменных
variables=(
    "BOT_TOKEN"
    "SERVER_IP" 
    "WEBAPP_URL"
    "BACKEND_URL"
    "BACKEND_PORT"
    "DB_EXTERNAL_PORT"
    "DB_INTERNAL_PORT"
    "POSTGRES_DB"
    "POSTGRES_USER"
    "POSTGRES_PASSWORD"
    "DATABASE_URL_INTERNAL"
    "ALLOWED_ORIGINS"
    "SECRET_KEY"
    "ENVIRONMENT"
    "LOG_LEVEL"
    "API_PREFIX"
    "BACKEND_HOST"
    "POSTGRES_VOLUME_NAME"
    "DOCKER_NETWORK_NAME"
    "GENERATE_TEST_DATA"
)

missing_vars=0

for var in "${variables[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ $var не установлена"
        missing_vars=$((missing_vars + 1))
    else
        echo "✅ $var = ${!var}"
    fi
done

echo ""
if [ $missing_vars -eq 0 ]; then
    echo "🎉 Все переменные установлены правильно!"
    
    echo ""
    echo "🔗 URLs для проверки после запуска:"
    echo "   Backend API: ${BACKEND_URL}/health"
    echo "   Backend Docs: ${BACKEND_URL}/docs" 
    echo "   Ngrok Frontend: ${WEBAPP_URL}"
    echo "   Database Port: ${SERVER_IP}:${DB_EXTERNAL_PORT}"
    
    echo ""
    echo "🚀 Готово к запуску:"
    echo "   docker-compose -f docker-compose.server.yml --env-file .env up -d"
    
else
    echo "❌ Найдено $missing_vars недостающих переменных!"
    echo "💡 Используйте ./scripts/setup-config.sh для настройки"
fi