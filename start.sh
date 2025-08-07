#!/bin/bash

echo "🚀 Запуск Social Rent App..."

# Создаем директории для логов
mkdir -p /var/log/supervisor

# Проверяем наличие .env файла
if [ ! -f "/app/.env" ]; then
    echo "⚠️ Файл .env не найден! Создаем базовую конфигурацию..."
    echo "❗ ОБЯЗАТЕЛЬНО отредактируйте файл .env перед запуском!"
    exit 1
fi

echo "📦 Устанавливаем зависимости..."

# Установка Python зависимостей для backend
if [ -f "/app/backend/requirements.txt" ]; then
    echo "📦 Устанавливаем Python зависимости..."
    cd /app && pip install -r backend/requirements.txt
fi

# Установка Python зависимостей для bot
if [ -f "/app/bot/requirements.txt" ]; then
    echo "🤖 Устанавливаем зависимости для бота..."
    cd /app && pip install -r bot/requirements.txt
fi

# Установка Node.js зависимостей для frontend
if [ -f "/app/frontend/package.json" ]; then
    echo "⚛️ Устанавливаем Node.js зависимости..."
    cd /app/frontend && yarn install
fi

echo "🏗️ Создаем сборку frontend..."
cd /app/frontend && yarn build

echo "📁 Копируем собранные файлы frontend в статическую папку..."
mkdir -p /app/static
cp -r /app/frontend/build/* /app/static/

echo "🔧 Запуск всех сервисов через supervisor..."

# Запуск supervisor с нашей конфигурацией
supervisord -c /app/supervisord.conf

echo "✅ Все сервисы запущены!"
echo ""
echo "🌐 Доступные URL:"
echo "   Приложение: http://localhost:8001"
echo "   API Health: http://localhost:8001/health"
echo "   API Docs:   http://localhost:8001/docs"
echo ""
echo "📊 Полезные команды:"
echo "   Статус:     supervisorctl status"
echo "   Перезапуск: supervisorctl restart all"
echo "   Логи:       tail -f /var/log/supervisor/*.log"