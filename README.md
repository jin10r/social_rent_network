# Social Rent App

Социальная сеть для поиска жилья и соседей через Telegram Web App.

## Структура проекта

- `backend/` - Бэкенд приложения (FastAPI)
- `frontend/` - Фронтенд приложения (React)
- `bot/` - Telegram бот (aiogram)
- `scripts/` - Скрипты для генерации тестовых данных

## Запуск приложения

1. Установите Docker и Docker Compose
2. Создайте .env файл с необходимыми переменными окружения
3. Запустите приложение:
   ```bash
   docker-compose up -d
   ```

## Настройка Telegram Web App

Telegram требует публичный HTTPS URL для Web App. Для локальной разработки используйте ngrok:

1. Установите ngrok: https://ngrok.com/download
2. Запустите ngrok:
   ```bash
   ngrok http 3000
   ```
3. Скопируйте HTTPS URL из вывода ngrok
4. Обновите WEBAPP_URL в docker-compose.yml на этот URL
5. Перезапустите контейнеры:
   ```bash
   docker-compose down && docker-compose up -d
   ```

## Генерация тестовых данных

```bash
# Запустить генерацию тестовых данных
./scripts/generate-test-data.sh

# Или через docker-compose
docker-compose run --rm test-data-generator python generate_test_data.py
```

## Переменные окружения

- `BOT_TOKEN` - Токен Telegram бота
- `WEBAPP_URL` - Публичный HTTPS URL для Web App (например, ngrok URL)
- `DATABASE_URL` - URL для подключения к PostgreSQL
- `BACKEND_URL` - URL бэкенда для бота
- `GENERATE_TEST_DATA` - (опционально) Установите в "true" для автоматической генерации тестовых данных при запуске бэкенда

## Решение проблем

### Telegram Web App URL Error

Если вы видите ошибку `Bad Request: inline keyboard button Web App URL is invalid`, убедитесь что:
1. Используется публичный HTTPS URL
2. URL не содержит localhost
3. URL корректно установлен в переменной окружения WEBAPP_URL

### Ошибки аутентификации

Если фронтенд не может получить доступ к API, проверьте:
1. Правильность токена Telegram Web App
2. Наличие пользователя в базе данных
3. Корректность передачи заголовков аутентификации
