#!/bin/bash

echo "⚙️ Помощник настройки конфигурации Social Rent App"
echo "=================================================="

# Функция для запроса ввода с проверкой
ask_input() {
    local prompt="$1"
    local var_name="$2"
    local default_value="$3"
    local current_value="$4"
    
    if [ -n "$current_value" ] && [ "$current_value" != "$default_value" ]; then
        echo "💡 Текущее значение $var_name: $current_value"
        read -p "$prompt [оставить текущее значение] или введите новое: " input
        if [ -z "$input" ]; then
            echo "$current_value"
        else
            echo "$input"
        fi
    else
        read -p "$prompt: " input
        echo "$input"
    fi
}

# Проверяем наличие .env файла
if [ -f ".env" ]; then
    echo "📋 Найден существующий .env файл"
    read -p "🤔 Хотите обновить настройки? (y/n): " update_config
    if [ "$update_config" != "y" ] && [ "$update_config" != "Y" ]; then
        echo "✅ Конфигурация оставлена без изменений"
        exit 0
    fi
    echo "🔄 Обновляем конфигурацию..."
else
    echo "📝 Создаем новый .env файл"
fi

# Получаем текущие значения из .env если он существует
if [ -f ".env" ]; then
    current_bot_token=$(grep "^BOT_TOKEN=" .env | cut -d'=' -f2)
    current_server_ip=$(grep "^SERVER_IP=" .env | cut -d'=' -f2)  
    current_webapp_url=$(grep "^WEBAPP_URL=" .env | cut -d'=' -f2)
    current_backend_url=$(grep "^BACKEND_URL=" .env | cut -d'=' -f2)
    current_bot_username=$(grep "^BOT_USERNAME=" .env | cut -d'=' -f2)
fi

echo ""
echo "🔑 ОСНОВНЫЕ НАСТРОЙКИ"
echo "===================="

# BOT_TOKEN
echo ""
echo "1️⃣ Токен Telegram бота"
echo "   📱 Получите у @BotFather в Telegram"
bot_token=$(ask_input "   Введите BOT_TOKEN" "BOT_TOKEN" "YOUR_TELEGRAM_BOT_TOKEN_HERE" "$current_bot_token")

# SERVER_IP  
echo ""
echo "2️⃣ IP адрес удаленного сервера"
echo "   🌐 IP где будет запущен backend и база данных"
server_ip=$(ask_input "   Введите SERVER_IP" "SERVER_IP" "YOUR_SERVER_IP_HERE" "$current_server_ip")

# BOT_USERNAME
echo ""
echo "3️⃣ Имя пользователя бота"  
echo "   👤 Имя бота без @ (например: my_social_rent_bot)"
bot_username=$(ask_input "   Введите BOT_USERNAME" "BOT_USERNAME" "social_rent_bot" "$current_bot_username")

echo ""
echo "🌐 NGROK НАСТРОЙКИ"
echo "=================="
echo ""
echo "4️⃣ Ngrok URL для frontend"
echo "   🔗 Сначала запустите: ngrok http 3000"
echo "   📋 Затем скопируйте HTTPS URL (например: https://abc123.ngrok-free.app)"
webapp_url=$(ask_input "   Введите WEBAPP_URL" "WEBAPP_URL" "YOUR_NGROK_FRONTEND_URL_HERE" "$current_webapp_url")

# Автоматически формируем другие URL на основе введенных данных
backend_url="http://${server_ip}:8001"
react_backend_url="http://${server_ip}:8001"
allowed_origins="http://localhost:3000,${webapp_url}"

echo ""
echo "✅ АВТОМАТИЧЕСКИ СФОРМИРОВАННЫЕ НАСТРОЙКИ:"
echo "   BACKEND_URL: $backend_url"
echo "   REACT_APP_BACKEND_URL: $react_backend_url"
echo "   ALLOWED_ORIGINS: $allowed_origins"

echo ""
read -p "💾 Сохранить конфигурацию? (y/n): " save_config
if [ "$save_config" != "y" ] && [ "$save_config" != "Y" ]; then
    echo "❌ Конфигурация не сохранена"
    exit 1
fi

# Создаем .env файл
echo "📝 Создание .env файла..."

cat > .env << EOF
# ==============================================================================
# ЦЕНТРАЛИЗОВАННАЯ КОНФИГУРАЦИЯ SOCIAL RENT APP
# ==============================================================================
# Создано автоматически $(date)

# ==============================================================================
# TELEGRAM BOT НАСТРОЙКИ
# ==============================================================================
BOT_TOKEN=$bot_token
BOT_USERNAME=$bot_username

# ==============================================================================
# СЕТЬ И URL НАСТРОЙКИ  
# ==============================================================================
SERVER_IP=$server_ip
WEBAPP_URL=$webapp_url
BACKEND_URL=$backend_url

# ==============================================================================
# ПОРТЫ КОНФИГУРАЦИЯ
# ==============================================================================
BACKEND_PORT=8001
FRONTEND_PORT=3000
DB_EXTERNAL_PORT=5432
DB_INTERNAL_PORT=5432

# ==============================================================================
# DATABASE НАСТРОЙКИ
# ==============================================================================
POSTGRES_DB=social_rent
POSTGRES_USER=postgres  
POSTGRES_PASSWORD=postgres123
DATABASE_URL_INTERNAL=postgresql+asyncpg://postgres:postgres123@db:5432/social_rent
DATABASE_URL_EXTERNAL=postgresql+asyncpg://postgres:postgres123@localhost:5432/social_rent

# ==============================================================================
# CORS И БЕЗОПАСНОСТЬ
# ==============================================================================  
ALLOWED_ORIGINS=$allowed_origins
SECRET_KEY=your_secret_key_change_in_production

# ==============================================================================
# ОКРУЖЕНИЕ И ЛОГИРОВАНИЕ
# ==============================================================================
ENVIRONMENT=development
LOG_LEVEL=INFO

# ==============================================================================
# API НАСТРОЙКИ
# ==============================================================================
API_PREFIX=/api
BACKEND_HOST=0.0.0.0

# ==============================================================================
# DOCKER И VOLUMES
# ==============================================================================
POSTGRES_VOLUME_NAME=social_rent_postgres_data
DOCKER_NETWORK_NAME=social_rent_network

# ==============================================================================
# ДОПОЛНИТЕЛЬНЫЕ НАСТРОЙКИ
# ==============================================================================
GENERATE_TEST_DATA=auto
REACT_APP_BACKEND_URL=$react_backend_url
REACT_APP_BOT_USERNAME=$bot_username
EOF

echo "✅ Конфигурация сохранена в .env файле!"
echo ""
echo "🚀 СЛЕДУЮЩИЕ ШАГИ:"
echo ""
echo "1️⃣ Запуск на сервере (bot + backend + database):"
echo "   ./scripts/server-start.sh"
echo ""
echo "2️⃣ Запуск локально (frontend):"
echo "   ./scripts/local-start.sh"
echo ""
echo "3️⃣ Проверка статуса всех сервисов:"
echo "   ./scripts/show-status.sh"
echo ""
echo "📚 Дополнительная документация:"
echo "   - CONFIG_GUIDE.md - краткий гайд по настройке"
echo "   - DEPLOYMENT_GUIDE.md - полное руководство по развертыванию"
echo "   - README.md - общая информация о проекте"