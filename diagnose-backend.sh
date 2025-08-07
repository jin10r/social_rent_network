#!/bin/bash

echo "🔍 Диагностика проблемы с backend контейнером..."

# Остановим текущие контейнеры
echo "🛑 Остановка текущих контейнеров..."
docker-compose -f docker-compose.server.yml down 2>/dev/null

echo "🧪 Запуск без health checks для диагностики..."
docker-compose -f docker-compose.test.yml --env-file .env up -d db

echo "⏳ Ожидание запуска базы данных (30 секунд)..."
sleep 30

echo "📊 Статус базы данных:"
docker-compose -f docker-compose.test.yml ps db

echo "🚀 Запуск backend..."
docker-compose -f docker-compose.test.yml --env-file .env up -d backend

echo "⏳ Ожидание запуска backend (30 секунд)..."
sleep 30

echo "📊 Статус backend:"
docker-compose -f docker-compose.test.yml ps backend

echo "📋 Логи backend за последние 50 строк:"
docker-compose -f docker-compose.test.yml logs --tail=50 backend

echo ""
echo "🔍 Проверка доступности backend:"
echo "Попытка подключения к http://localhost:8001/health..."

# Попытка проверить health endpoint
if docker exec social_rent_backend python -c "
import requests
import sys
try:
    response = requests.get('http://localhost:8001/health', timeout=5)
    print(f'✅ Health check успешен: {response.status_code}')
    print(f'Response: {response.text}')
except Exception as e:
    print(f'❌ Health check failed: {e}')
    sys.exit(1)
" 2>/dev/null; then
    echo "✅ Backend отвечает на health check"
else
    echo "❌ Backend не отвечает на health check"
    
    echo ""
    echo "🔍 Дополнительная диагностика:"
    echo "Проверка процессов в контейнере:"
    docker exec social_rent_backend ps aux || echo "Не удалось получить список процессов"
    
    echo ""
    echo "Проверка портов:"
    docker exec social_rent_backend netstat -tlnp || echo "Не удалось получить список портов"
fi

echo ""
echo "🔍 Проверка подключения к базе данных:"
if docker exec social_rent_db pg_isready -U postgres -d social_rent; then
    echo "✅ База данных готова к подключению"
else
    echo "❌ База данных не готова"
fi

echo ""
echo "📝 Рекомендации:"
echo "1. Проверьте логи backend выше"
echo "2. Убедитесь, что база данных запущена и доступна"
echo "3. Проверьте переменные окружения в .env"
echo "4. При необходимости исправьте проблемы и перезапустите"