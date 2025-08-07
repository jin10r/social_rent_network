#!/bin/bash

echo "📊 Статус сервисов Social Rent App"
echo "=================================="

# Проверка серверных сервисов
if [ -f "docker-compose.server.yml" ]; then
    echo ""
    echo "🖥️  СЕРВЕРНЫЕ СЕРВИСЫ:"
    if docker-compose -f docker-compose.server.yml ps | grep -q "Up"; then
        docker-compose -f docker-compose.server.yml ps
        
        echo ""
        echo "🔍 Health Checks:"
        
        # Проверка backend
        BACKEND_URL=$(grep BACKEND_URL .env | cut -d'=' -f2 2>/dev/null || echo "http://localhost:8001")
        if curl -s "$BACKEND_URL/health" > /dev/null 2>&1; then
            echo "   ✅ Backend: $BACKEND_URL/health - OK"
        else
            echo "   ❌ Backend: $BACKEND_URL/health - недоступен"
        fi
        
    else
        echo "   ❌ Серверные сервисы не запущены"
        echo "   💡 Запустите: ./scripts/server-start.sh"
    fi
else
    echo "   ⚠️  docker-compose.server.yml не найден"
fi

# Проверка локальных сервисов  
if [ -f "docker-compose.local.yml" ]; then
    echo ""
    echo "💻 ЛОКАЛЬНЫЕ СЕРВИСЫ:"
    if docker-compose -f docker-compose.local.yml ps | grep -q "Up"; then
        docker-compose -f docker-compose.local.yml ps
        
        echo ""
        echo "🔍 Health Checks:"
        
        # Проверка frontend
        if curl -s "http://localhost:3000" > /dev/null 2>&1; then
            echo "   ✅ Frontend: http://localhost:3000 - OK"
        else
            echo "   ❌ Frontend: http://localhost:3000 - недоступен"
        fi
        
    else
        echo "   ❌ Локальные сервисы не запущены"
        echo "   💡 Запустите: ./scripts/local-start.sh"
    fi
else
    echo "   ⚠️  docker-compose.local.yml не найден"
fi

# Проверка конфигурации
echo ""
echo "⚙️  КОНФИГУРАЦИЯ:"
if [ -f ".env" ]; then
    echo "   ✅ .env файл найден"
    
    # Проверка основных переменных
    if grep -q "YOUR_TELEGRAM_BOT_TOKEN_HERE" .env 2>/dev/null; then
        echo "   ⚠️  BOT_TOKEN требует настройки"
    else
        echo "   ✅ BOT_TOKEN настроен"
    fi
    
    if grep -q "YOUR_SERVER_IP_HERE" .env 2>/dev/null; then
        echo "   ⚠️  SERVER_IP требует настройки"
    else
        SERVER_IP=$(grep SERVER_IP .env | cut -d'=' -f2 2>/dev/null)
        echo "   ✅ SERVER_IP: $SERVER_IP"
    fi
    
    if grep -q "YOUR_NGROK_FRONTEND_URL_HERE" .env 2>/dev/null; then
        echo "   ⚠️  WEBAPP_URL требует настройки"
    else
        WEBAPP_URL=$(grep WEBAPP_URL .env | cut -d'=' -f2 2>/dev/null)
        echo "   ✅ WEBAPP_URL: $WEBAPP_URL"
    fi
    
else
    echo "   ❌ .env файл не найден"
    echo "   💡 Создайте из шаблона и настройте переменные"
fi

echo ""
echo "📚 ПОЛЕЗНЫЕ КОМАНДЫ:"
echo "   Запуск сервера:     ./scripts/server-start.sh"
echo "   Запуск локально:    ./scripts/local-start.sh"
echo "   Перезапуск сервера: ./scripts/server-restart.sh"
echo "   Просмотр логов:     docker-compose -f docker-compose.server.yml logs -f"
echo "   Остановка всего:    ./scripts/stop-all.sh"