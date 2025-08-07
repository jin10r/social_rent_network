#!/bin/bash

echo "🔍 Проверка конфигурации Social Rent App..."
echo "================================================"

# Проверка наличия необходимых файлов
echo "📁 Проверка файлов:"
files=(
    "docker-compose.yml"
    "nginx.conf"
    ".env"
    "backend/Dockerfile"
    "frontend/Dockerfile"
    "bot/Dockerfile"
    "backend/main.py"
    "frontend/src/services/api.js"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file - найден"
    else
        echo "  ❌ $file - НЕ НАЙДЕН"
    fi
done

echo ""
echo "📋 Проверка docker-compose.yml:"
if [ -f "docker-compose.yml" ]; then
    # Проверка наличия всех сервисов
    services=("nginx" "db" "backend" "frontend" "bot")
    for service in "${services[@]}"; do
        if grep -q "^  $service:" docker-compose.yml; then
            echo "  ✅ Сервис $service - настроен"
        else
            echo "  ❌ Сервис $service - НЕ НАЙДЕН"
        fi
    done
else
    echo "  ❌ docker-compose.yml не найден"
fi

echo ""
echo "🌐 Проверка nginx конфигурации:"
if [ -f "nginx.conf" ]; then
    if grep -q "location /api/" nginx.conf; then
        echo "  ✅ Маршрутизация /api/ на backend - настроена"
    else
        echo "  ❌ Маршрутизация /api/ - НЕ НАЙДЕНА"
    fi
    
    if grep -q "location / {" nginx.conf; then
        echo "  ✅ Маршрутизация / на frontend - настроена"
    else
        echo "  ❌ Маршрутизация / - НЕ НАЙДЕНА"
    fi
else
    echo "  ❌ nginx.conf не найден"
fi

echo ""
echo "⚙️  Проверка переменных окружения:"
if [ -f ".env" ]; then
    env_vars=("BOT_TOKEN" "WEBAPP_URL" "REACT_APP_BACKEND_URL" "NGINX_PORT")
    for var in "${env_vars[@]}"; do
        if grep -q "^$var=" .env; then
            echo "  ✅ $var - настроена"
        else
            echo "  ❌ $var - НЕ НАЙДЕНА"
        fi
    done
else
    echo "  ❌ .env файл не найден"
fi

echo ""
echo "🚀 Команды для запуска:"
echo "  docker compose up -d          # Запуск всех сервисов"
echo "  docker compose logs -f        # Просмотр логов"
echo "  docker compose ps             # Статус сервисов"
echo "  docker compose down           # Остановка"

echo ""
echo "🌐 Доступ к приложению после запуска:"
echo "  Главная страница:    http://localhost:8080"
echo "  Backend API:         http://localhost:8080/api/"
echo "  API документация:    http://localhost:8080/docs"
echo "  Health check:        http://localhost:8080/health"

echo ""
echo "✅ Конфигурация проверена!"