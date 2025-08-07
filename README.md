# Social Rent App

Социальная сеть для поиска жилья и соседей через Telegram Web App.

## 🏗️ Архитектура приложения

- `backend/` - Backend приложения (FastAPI + PostgreSQL)
- `frontend/` - Frontend приложения (React)  
- `bot/` - Telegram бот (aiogram)
- `nginx.conf` - Nginx reverse proxy конфигурация
- `docker-compose.yml` - Единый файл для деплоя всех сервисов

## ✅ Что готово

- ✅ **Nginx Reverse Proxy** - единая точка входа на порту 8080
- ✅ **Централизованная конфигурация** - все настройки в файле `.env`
- ✅ **Единый Docker Compose** - все сервисы в одном файле
- ✅ **Автоматическая маршрутизация** - /api/* → backend, /* → frontend
- ✅ **Health checks** - проверка готовности всех сервисов
- ✅ **Готов к деплою** - единственная команда для запуска

## 🚀 Быстрый запуск

### 1. Настройка конфигурации

Отредактируйте файл `.env` - укажите ваши настройки:

```env
# Основные настройки для изменения:
BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_HERE
WEBAPP_URL=http://localhost:8080  # или ваш ngrok/публичный URL
REACT_APP_BOT_USERNAME=YOUR_BOT_USERNAME_HERE
```

### 2. Запуск всех сервисов

```bash
# Запуск всех сервисов (nginx + backend + frontend + database + bot)
docker-compose up -d

# Просмотр логов всех сервисов
docker-compose logs -f

# Остановка всех сервисов
docker-compose down
```

### 3. Доступ к приложению

- **Главное приложение**: http://localhost:8080
- **Backend API**: http://localhost:8080/api/
- **API документация**: http://localhost:8080/docs
- **Health check**: http://localhost:8080/health

## 🌐 Настройка для продакшна

Для работы Telegram Web App в продакшне требуется HTTPS:

1. Установите ngrok: https://ngrok.com/download
2. Запустите ngrok:
   ```bash
   ngrok http 8080
   ```
3. Скопируйте HTTPS URL (например: `https://abc123.ngrok-free.app`)
4. Обновите в `.env`:
   ```env
   WEBAPP_URL=https://abc123.ngrok-free.app
   REACT_APP_BACKEND_URL=https://abc123.ngrok-free.app
   ALLOWED_ORIGINS=https://abc123.ngrok-free.app,http://localhost:8080
   ```
5. Перезапустите сервисы:
   ```bash
   docker-compose restart
   ```

## 🔧 Полезные команды

### Мониторинг сервисов

```bash
# Статус всех сервисов
docker-compose ps

# Логи конкретного сервиса
docker-compose logs nginx
docker-compose logs backend
docker-compose logs frontend
docker-compose logs bot
docker-compose logs db

# Health check всех сервисов
curl http://localhost:8080/health  # backend через nginx
curl http://localhost:8080         # frontend через nginx
```

### Работа с базой данных

```bash
# Подключение к базе данных
docker exec -it social_rent_db psql -U postgres -d social_rent

# Генерация тестовых данных вручную
docker-compose exec backend python /app/generate_test_data.py
```

### Разработка

```bash
# Перезапуск отдельного сервиса
docker-compose restart backend
docker-compose restart frontend
docker-compose restart nginx

# Пересборка после изменения кода
docker-compose up --build -d
```

### Очистка системы

```bash
# Полная остановка и очистка
docker-compose down -v

# Очистка образов и volumes
docker system prune -a
docker volume prune
```

## 📊 Основные переменные окружения

| Переменная | Описание | Пример |
|------------|----------|---------|
| `BOT_TOKEN` | Токен Telegram бота от @BotFather | `123456789:ABC...` |
| `WEBAPP_URL` | URL для Telegram Web App | `http://localhost:8080` |
| `REACT_APP_BOT_USERNAME` | Username бота (без @) | `my_social_rent_bot` |
| `NGINX_PORT` | Порт nginx (главная точка входа) | `8080` |
| `REACT_APP_BACKEND_URL` | URL backend API для фронтенда | `http://localhost:8080` |

## 🛠️ Архитектура nginx routing

```
http://localhost:8080/api/*     → backend:8001  (FastAPI)
http://localhost:8080/health    → backend:8001  (Health check)
http://localhost:8080/docs      → backend:8001  (API docs)
http://localhost:8080/*         → frontend:3000 (React)
```

## 🚨 Решение проблем

### Сервисы не запускаются
```bash
# Проверьте статус и логи
docker-compose ps
docker-compose logs

# Пересоберите контейнеры
docker-compose up --build -d
```

### Ошибки Telegram Web App
- Убедитесь, что `WEBAPP_URL` использует HTTPS в продакшне
- URL не должен содержать localhost для внешнего доступа
- Перезапустите бот после изменения `WEBAPP_URL`

### CORS ошибки  
- Добавьте все необходимые URL в `ALLOWED_ORIGINS`
- Перезапустите все сервисы после изменения настроек

### Проблемы с портами
- Убедитесь, что порт 8080 свободен: `lsof -i :8080`
- Измените `NGINX_PORT` в `.env` при необходимости

## 🔒 Безопасность

Для production обязательно измените:
- `BOT_TOKEN` - на настоящий токен от @BotFather
- `SECRET_KEY` - на надежный секретный ключ (генерируйте случайно)
- `POSTGRES_PASSWORD` - на сильный пароль
- `ALLOWED_ORIGINS` - ограничьте конкретными доменами
- `ENVIRONMENT=production` и `LOG_LEVEL=WARNING`
- Используйте HTTPS для `WEBAPP_URL` и всех URL

Единый docker-compose.yml с nginx reverse proxy готов к использованию!