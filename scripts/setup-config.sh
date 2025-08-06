#!/bin/bash

# ==========================================
# СКРИПТ НАСТРОЙКИ КОНФИГУРАЦИИ
# ==========================================
# Этот скрипт помогает быстро настроить конфигурацию

set -e

echo "🚀 Social Rent App - Настройка конфигурации"
echo "=============================================="

# Проверка наличия .env файла
if [ ! -f .env ]; then
    echo "📋 Создание .env файла из шаблона..."
    cp .env.central .env
    echo "✅ Файл .env создан"
else
    echo "⚠️  Файл .env уже существует"
    read -p "Перезаписать? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp .env.central .env
        echo "✅ Файл .env обновлен"
    fi
fi

# Интерактивная настройка основных переменных
echo
echo "🔧 Настройка основных параметров:"
echo

read -p "Введите токен Telegram бота (или нажмите Enter для пропуска): " bot_token
if [ ! -z "$bot_token" ]; then
    sed -i "s/BOT_TOKEN=.*/BOT_TOKEN=$bot_token/" .env
    echo "✅ BOT_TOKEN обновлен"
fi

read -p "Введите URL веб-приложения (https://12345.ngrok-free.app): " webapp_url
if [ ! -z "$webapp_url" ]; then
    sed -i "s|WEBAPP_URL=.*|WEBAPP_URL=$webapp_url|" .env
    echo "✅ WEBAPP_URL обновлен"
fi

read -p "Введите URL backend сервера (http://your-ip:8001): " backend_url  
if [ ! -z "$backend_url" ]; then
    sed -i "s|BACKEND_URL=.*|BACKEND_URL=$backend_url|" .env
    echo "✅ BACKEND_URL обновлен"
fi

read -p "Введите разрешенные источники для CORS (через запятую): " allowed_origins
if [ ! -z "$allowed_origins" ]; then
    sed -i "s|ALLOWED_ORIGINS=.*|ALLOWED_ORIGINS=$allowed_origins|" .env
    echo "✅ ALLOWED_ORIGINS обновлен"
fi

echo
echo "✅ Конфигурация настроена!"
echo "📝 Файл .env готов к использованию"
echo
echo "Следующие шаги:"
echo "1. Проверьте настройки в .env файле"
echo "2. Запустите сервисы командой:"
echo "   ./scripts/start-remote.sh  # для удаленного сервера"
echo "   ./scripts/start-frontend.sh  # для локального фронтенда"