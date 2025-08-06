# Конфигурация Social Rent App

## Обзор

Этот документ описывает конфигурацию Social Rent App и как управлять настройками приложения.

## Файлы конфигурации

### app.env

Основной файл конфигурации, содержащий все основные настройки приложения:

```env
# PostgreSQL Database Configuration
DATABASE_URL=postgresql+asyncpg://postgres:postgres123@localhost:5433/social_rent
DATABASE_URL_INTERNAL=postgresql+asyncpg://postgres:postgres123@db:5432/social_rent

# Telegram Bot Configuration
BOT_TOKEN=your_telegram_bot_token_here
WEBAPP_URL=https://your-ngrok-url.ngrok-free.app
BACKEND_URL=http://localhost:8001

# Environment
ENVIRONMENT=development

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,https://localhost:3000

# Security
SECRET_KEY=your_secret_key_here_change_in_production

# API Configuration
API_PREFIX=/api
HOST=0.0.0.0
PORT=8001

# Logging
LOG_LEVEL=INFO

# Ports Configuration
DB_EXTERNAL_PORT=5433
DB_INTERNAL_PORT=5432
BACKEND_PORT=8001
FRONTEND_PORT=3000
```

### backend/.env.example

Пример файла конфигурации для бэкенда:

```env
# PostgreSQL Database Configuration
DATABASE_URL=${DATABASE_URL_EXTERNAL:-postgresql+asyncpg://postgres:postgres123@localhost:5433/social_rent}
DATABASE_URL_INTERNAL=postgresql+asyncpg://postgres:postgres123@db:5432/social_rent

# Telegram Bot Configuration
BOT_TOKEN=${BOT_TOKEN}
WEBAPP_URL=${WEBAPP_URL:-https://your-ngrok-url.ngrok-free.app}
BACKEND_URL=${BACKEND_URL:-http://localhost:8001}

# Environment
ENVIRONMENT=${ENVIRONMENT:-development}

# CORS Configuration
ALLOWED_ORIGINS=${ALLOWED_ORIGINS:-http://localhost:3000,https://localhost:3000}

# Security
SECRET_KEY=${SECRET_KEY:-your_secret_key_here_change_in_production}

# API Configuration
API_PREFIX=${API_PREFIX:-/api}
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8001}

# Logging
LOG_LEVEL=${LOG_LEVEL:-INFO}

# Ports Configuration
DB_EXTERNAL_PORT=${DB_EXTERNAL_PORT:-5433}
DB_INTERNAL_PORT=${DB_INTERNAL_PORT:-5432}
BACKEND_PORT=${BACKEND_PORT:-8001}
FRONTEND_PORT=${FRONTEND_PORT:-3000}
```

## Переменные окружения Docker Compose

Все docker-compose файлы используют переменные окружения из `app.env`:

- `DATABASE_URL_INTERNAL` - URL для подключения к базе данных внутри контейнеров
- `BOT_TOKEN` - Токен Telegram бота
- `WEBAPP_URL` - Публичный URL для Web App
- `BACKEND_PORT` - Порт бэкенда

## Порты

- База данных внешний порт: 5433 (вместо 5432 для избежания конфликтов)
- База данных внутренний порт: 5432 (внутри контейнера)
- Бэкенд: 8001
- Фронтенд: 3000

## Настройка приложения

1. Скопируйте `app.env` в `.env` и настройте переменные:
   ```bash
   cp app.env .env
   # Отредактируйте .env файл
   ```

2. Запустите приложение:
   ```bash
   docker-compose --env-file .env up -d
   ```

## Решение проблем

### Порт 5432 уже используется

Если вы получаете ошибку о том, что порт 5432 уже используется:

1. Убедитесь, что в `app.env` установлен `DB_EXTERNAL_PORT=5433`
2. Проверьте, что в docker-compose.yml порт базы данных настроен как `"5433:5432"`

### Ошибка подключения к базе данных

1. Проверьте, что `DATABASE_URL_INTERNAL` в `app.env` корректен
2. Убедитесь, что сервис `db` запущен в docker-compose

### Ошибка Telegram Web App

1. Убедитесь, что `WEBAPP_URL` в `app.env` указывает на правильный публичный URL (например, ngrok)
2. Проверьте, что URL использует HTTPS и не содержит localhost
