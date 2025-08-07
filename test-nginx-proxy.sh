#!/bin/bash

echo "🧪 Тестирование nginx reverse proxy..."
echo "====================================="

NGINX_URL="http://localhost:8080"

echo "🌐 Проверка доступности nginx..."
if curl -s --max-time 5 "$NGINX_URL" > /dev/null; then
    echo "  ✅ Nginx доступен на $NGINX_URL"
else
    echo "  ❌ Nginx недоступен на $NGINX_URL"
    echo "  💡 Запустите: docker compose up -d"
    exit 1
fi

echo ""
echo "🔍 Тестирование маршрутизации API (backend)..."

# Тест health check endpoint
echo "  📊 Health check: $NGINX_URL/health"
response=$(curl -s -w "%{http_code}" "$NGINX_URL/health")
http_code="${response: -3}"
if [ "$http_code" = "200" ]; then
    echo "    ✅ Health check работает (HTTP $http_code)"
else
    echo "    ❌ Health check не работает (HTTP $http_code)"
fi

# Тест API документации
echo "  📚 API docs: $NGINX_URL/docs"
response=$(curl -s -w "%{http_code}" "$NGINX_URL/docs")
http_code="${response: -3}"
if [ "$http_code" = "200" ]; then
    echo "    ✅ API документация доступна (HTTP $http_code)"
else
    echo "    ❌ API документация недоступна (HTTP $http_code)"
fi

# Тест metro stations API
echo "  🚇 Metro API: $NGINX_URL/api/metro/stations"
response=$(curl -s -w "%{http_code}" "$NGINX_URL/api/metro/stations")
http_code="${response: -3}"
if [ "$http_code" = "200" ]; then
    echo "    ✅ Metro API работает (HTTP $http_code)"
else
    echo "    ❌ Metro API не работает (HTTP $http_code)"
fi

echo ""
echo "🎨 Тестирование маршрутизации frontend..."

# Тест главной страницы
echo "  🏠 Главная страница: $NGINX_URL/"
response=$(curl -s -w "%{http_code}" "$NGINX_URL/")
http_code="${response: -3}"
if [ "$http_code" = "200" ]; then
    echo "    ✅ Frontend доступен (HTTP $http_code)"
else
    echo "    ❌ Frontend недоступен (HTTP $http_code)"
fi

# Тест статических ресурсов
echo "  📦 Статические ресурсы (должны проксироваться на frontend)"
if curl -s --max-time 5 "$NGINX_URL/static" > /dev/null; then
    echo "    ✅ Статические ресурсы доступны"
else
    echo "    ℹ️  Статические ресурсы будут доступны после сборки React"
fi

echo ""
echo "📊 Проверка заголовков proxy..."
headers=$(curl -s -I "$NGINX_URL/health")
if echo "$headers" | grep -q "X-Forwarded-For"; then
    echo "  ✅ Proxy заголовки настроены"
else
    echo "  ⚠️  Proxy заголовки могут отсутствовать"
fi

echo ""
echo "🔧 Диагностическая информация:"
echo "  • Nginx порт: 8080"
echo "  • Backend проксирование: /api/* → backend:8001"
echo "  • Frontend проксирование: /* → frontend:3000"
echo ""
echo "📋 Полезные команды:"
echo "  docker compose logs nginx    # Логи nginx"
echo "  docker compose logs backend  # Логи backend"
echo "  docker compose logs frontend # Логи frontend"
echo "  docker compose ps            # Статус всех сервисов"
echo ""
echo "✅ Тестирование завершено!"