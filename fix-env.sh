#!/bin/bash

echo "🔧 Автоматическое исправление .env файла..."

# Проверим текущий .env файл
if [ -f ".env" ]; then
    echo "📋 Обнаружен существующий .env файл"
    
    # Сделаем резервную копию
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
    echo "💾 Создана резервная копия .env файла"
    
    # Проверим, есть ли недостающие переменные
    missing_vars=()
    
    # Список обязательных переменных
    required_vars=(
        "BACKEND_PORT"
        "FRONTEND_PORT"
        "DB_INTERNAL_PORT"
        "POSTGRES_DB"
        "POSTGRES_USER"
        "API_PREFIX"
        "BACKEND_HOST"
        "SECRET_KEY"
        "ENVIRONMENT"
        "LOG_LEVEL"
        "GENERATE_TEST_DATA"
        "POSTGRES_VOLUME_NAME"
        "DOCKER_NETWORK_NAME"
        "REACT_APP_BACKEND_URL"
        "REACT_APP_BOT_USERNAME"
    )
    
    for var in "${required_vars[@]}"; do
        if ! grep -q "^${var}=" .env; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -gt 0 ]; then
        echo "⚠️  Найдены недостающие переменные: ${missing_vars[*]}"
        echo "🔄 Добавляю недостающие переменные..."
        
        # Добавляем недостающие переменные
        for var in "${missing_vars[@]}"; do
            case $var in
                "BACKEND_PORT")
                    echo "BACKEND_PORT=8001" >> .env
                    ;;
                "FRONTEND_PORT")
                    echo "FRONTEND_PORT=3000" >> .env
                    ;;
                "DB_INTERNAL_PORT")
                    echo "DB_INTERNAL_PORT=5432" >> .env
                    ;;
                "POSTGRES_DB")
                    echo "POSTGRES_DB=social_rent" >> .env
                    ;;
                "POSTGRES_USER")
                    echo "POSTGRES_USER=postgres" >> .env
                    ;;
                "API_PREFIX")
                    echo "API_PREFIX=/api" >> .env
                    ;;
                "BACKEND_HOST")
                    echo "BACKEND_HOST=0.0.0.0" >> .env
                    ;;
                "SECRET_KEY")
                    echo "SECRET_KEY=your_secret_key_change_in_production" >> .env
                    ;;
                "ENVIRONMENT")
                    echo "ENVIRONMENT=development" >> .env
                    ;;
                "LOG_LEVEL")
                    echo "LOG_LEVEL=INFO" >> .env
                    ;;
                "GENERATE_TEST_DATA")
                    echo "GENERATE_TEST_DATA=auto" >> .env
                    ;;
                "POSTGRES_VOLUME_NAME")
                    echo "POSTGRES_VOLUME_NAME=social_rent_postgres_data" >> .env
                    ;;
                "DOCKER_NETWORK_NAME")
                    echo "DOCKER_NETWORK_NAME=social_rent_network" >> .env
                    ;;
                "REACT_APP_BACKEND_URL")
                    if grep -q "^BACKEND_URL=" .env; then
                        backend_url=$(grep "^BACKEND_URL=" .env | cut -d'=' -f2)
                        echo "REACT_APP_BACKEND_URL=$backend_url" >> .env
                    else
                        echo "REACT_APP_BACKEND_URL=http://YOUR_SERVER_IP:8001" >> .env
                    fi
                    ;;
                "REACT_APP_BOT_USERNAME")
                    if grep -q "^BOT_USERNAME=" .env; then
                        bot_username=$(grep "^BOT_USERNAME=" .env | cut -d'=' -f2)
                        echo "REACT_APP_BOT_USERNAME=$bot_username" >> .env
                    else
                        echo "REACT_APP_BOT_USERNAME=social_rent_bot" >> .env
                    fi
                    ;;
            esac
        done
        
        # Если нет DATABASE_URL_INTERNAL, создадим её
        if ! grep -q "^DATABASE_URL_INTERNAL=" .env; then
            if grep -q "^POSTGRES_PASSWORD=" .env; then
                db_password=$(grep "^POSTGRES_PASSWORD=" .env | cut -d'=' -f2)
                echo "DATABASE_URL_INTERNAL=postgresql+asyncpg://postgres:$db_password@db:5432/social_rent" >> .env
            fi
        fi
        
        echo "✅ Недостающие переменные добавлены"
    else
        echo "✅ Все необходимые переменные найдены"
    fi
    
else
    echo "❌ Файл .env не найден!"
    echo "💡 Запустите ./scripts/setup-config.sh для создания конфигурации"
    exit 1
fi

echo ""
echo "🧪 Тестирование исправленной конфигурации..."
./test-config.sh