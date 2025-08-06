#!/bin/bash

# ==========================================
# СКРИПТ МОНИТОРИНГА СЕРВИСОВ
# ==========================================
# Проверяет статус всех сервисов

set -e

echo "📊 Social Rent App - Мониторинг сервисов"
echo "========================================"

# Проверка наличия .env файла
if [ ! -f .env ]; then
    echo "❌ Файл .env не найден!"
    exit 1
fi

source .env

echo "🔍 Проверка удаленного сервера:"
echo "--------------------------------"

# Проверка статуса контейнеров удаленного сервера
if docker-compose -f docker-compose.remote.yml ps | grep -q "Up"; then
    echo "📦 Статус контейнеров удаленного сервера:"
    docker-compose -f docker-compose.remote.yml ps
    echo
    
    # Проверка health checks
    echo "🏥 Health checks удаленного сервера:"
    
    # База данных
    if docker-compose -f docker-compose.remote.yml exec -T db pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB} >/dev/null 2>&1; then
        echo "✅ База данных: OK"
    else
        echo "❌ База данных: FAIL"
    fi
    
    # Backend
    if curl -f http://localhost:${BACKEND_PORT}/health >/dev/null 2>&1; then
        echo "✅ Backend API: OK (http://localhost:${BACKEND_PORT}/health)"
    else
        echo "❌ Backend API: FAIL"
    fi
    
    # Проверка bot процесса
    if docker-compose -f docker-compose.remote.yml exec -T bot pgrep -f 'python.*main.py' >/dev/null 2>&1; then
        echo "✅ Telegram Bot: OK"
    else
        echo "❌ Telegram Bot: FAIL"
    fi
else
    echo "❌ Сервисы удаленного сервера не запущены"
fi

echo
echo "🔍 Проверка локального фронтенда:"
echo "---------------------------------"

# Проверка статуса фронтенда
if docker-compose -f docker-compose.frontend.yml ps | grep -q "Up"; then
    echo "📦 Статус контейнера фронтенда:"
    docker-compose -f docker-compose.frontend.yml ps
    echo
    
    # Проверка доступности фронтенда
    echo "🏥 Health check фронтенда:"
    if curl -f http://localhost:${FRONTEND_PORT} >/dev/null 2>&1; then
        echo "✅ Frontend: OK (http://localhost:${FRONTEND_PORT})"
    else
        echo "❌ Frontend: FAIL"
    fi
else
    echo "❌ Фронтенд не запущен"
fi

echo
echo "🌐 Проверка внешних подключений:"
echo "--------------------------------"

# Проверка backend URL
backend_host=$(echo $BACKEND_URL | sed 's|http://||' | sed 's|https://||' | cut -d: -f1)
backend_port=$(echo $BACKEND_URL | sed 's|.*:||')

if timeout 5 bash -c "</dev/tcp/$backend_host/$backend_port" 2>/dev/null; then
    echo "✅ Backend URL доступен: $BACKEND_URL"
else
    echo "❌ Backend URL недоступен: $BACKEND_URL"
fi

# Проверка webapp URL
if curl -f "$WEBAPP_URL" >/dev/null 2>&1; then
    echo "✅ Webapp URL доступен: $WEBAPP_URL"
else
    echo "❌ Webapp URL недоступен: $WEBAPP_URL"
fi

echo
echo "💾 Использование ресурсов:"
echo "--------------------------"

# Docker статистика
echo "📈 Docker контейнеры:"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" | grep social_rent || echo "Контейнеры не найдены"

echo
echo "🗄️  Использование дискового пространства:"
docker system df

echo
echo "📝 Последние логи (последние 5 строк):"
echo "--------------------------------------"

if docker-compose -f docker-compose.remote.yml ps | grep -q "Up"; then
    echo "🔧 Backend:"
    docker-compose -f docker-compose.remote.yml logs --tail=5 backend 2>/dev/null || echo "Логи недоступны"
    
    echo "🤖 Bot:"  
    docker-compose -f docker-compose.remote.yml logs --tail=5 bot 2>/dev/null || echo "Логи недоступны"
fi

if docker-compose -f docker-compose.frontend.yml ps | grep -q "Up"; then
    echo "🎨 Frontend:"
    docker-compose -f docker-compose.frontend.yml logs --tail=5 frontend 2>/dev/null || echo "Логи недоступны"
fi

echo
echo "✅ Мониторинг завершен"