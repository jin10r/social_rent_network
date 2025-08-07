# Social Rent App

Социальная сеть для поиска жилья и соседей через Telegram Web App.

## 🏗️ Архитектура приложения

- `backend/` - Backend приложения (FastAPI + PostgreSQL)
- `frontend/` - Frontend приложения (React)  
- `bot/` - Telegram бот (aiogram)
- `scripts/` - Служебные скрипты

## ✅ Что готово

- ✅ **Централизованная конфигурация** - все настройки в файле `.env`
- ✅ **2 Docker Compose файла**:
  - `docker-compose.server.yml` - сервер (bot + backend + database)
  - `docker-compose.local.yml` - локальная машина (frontend)
- ✅ **Удалены лишние файлы** - оставлены только необходимые
- ✅ **Готов к деплою** - можно сразу использовать на двух машинах

## 🚀 Быстрый запуск

### 1. Настройка конфигурации

Отредактируйте файл `.env` - укажите ваши настройки:

```env
# Основные настройки для изменения:
BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_HERE
SERVER_IP=YOUR_SERVER_IP_HERE  
WEBAPP_URL=YOUR_NGROK_FRONTEND_URL_HERE
BACKEND_URL=http://YOUR_SERVER_IP_HERE:8001
ALLOWED_ORIGINS=http://localhost:3000,YOUR_NGROK_FRONTEND_URL_HERE
```

### 2. Запуск на удаленном сервере (bot + backend + база данных)

```bash
# На удаленном сервере
docker-compose -f docker-compose.server.yml --env-file .env up -d

# Просмотр логов всех сервисов
docker-compose -f docker-compose.server.yml logs -f

# Остановка
docker-compose -f docker-compose.server.yml down
```

### 3. Запуск локального frontend

```bash
# На локальной машине
docker-compose -f docker-compose.local.yml --env-file .env up -d

# Просмотр логов frontend
docker-compose -f docker-compose.local.yml logs -f

# Остановка
docker-compose -f docker-compose.local.yml down
```

## 🌐 Настройка Ngrok

Для работы Telegram Web App требуется публичный HTTPS URL:

1. Установите ngrok: https://ngrok.com/download
2. Запустите ngrok для frontend:
   ```bash
   ngrok http 3000
   ```
3. Скопируйте HTTPS URL (например: `https://abc123.ngrok-free.app`)
4. Обновите в `.env`:
   ```env
   WEBAPP_URL=https://abc123.ngrok-free.app
   ALLOWED_ORIGINS=http://localhost:3000,https://abc123.ngrok-free.app
   ```
5. Перезапустите сервисы:
   ```bash
   # На сервере
   docker-compose -f docker-compose.server.yml restart
   ```

## 🔧 Полезные команды

### Мониторинг сервисов

```bash
# Статус сервисов на сервере
docker-compose -f docker-compose.server.yml ps

# Статус локального frontend
docker-compose -f docker-compose.local.yml ps

# Health check
curl http://YOUR_SERVER_IP:8001/health  # backend
curl http://localhost:3000              # frontend
```

### Работа с базой данных

```bash
# Подключение к базе данных
docker exec -it social_rent_db psql -U postgres -d social_rent

# Генерация тестовых данных вручную
docker-compose -f docker-compose.server.yml exec backend python /app/generate_test_data.py
```

### Очистка системы

```bash
# Полная остановка и очистка
docker-compose -f docker-compose.server.yml down -v
docker-compose -f docker-compose.local.yml down -v

# Очистка образов
docker system prune -a
```

## 📊 Основные переменные окружения

| Переменная | Описание | Пример |
|------------|----------|---------|
| `BOT_TOKEN` | Токен Telegram бота от @BotFather | `123456789:ABC...` |
| `SERVER_IP` | IP адрес удаленного сервера | `185.36.141.151` |
| `WEBAPP_URL` | HTTPS URL для Telegram Web App | `https://abc.ngrok-free.app` |
| `BACKEND_URL` | URL backend API | `http://185.36.141.151:8001` |
| `ALLOWED_ORIGINS` | Разрешенные CORS источники | `http://localhost:3000,https://...` |

## 🛠️ Сценарии развертывания

### Вариант 1: Полная локальная разработка
```bash
# Запустить все сервисы локально (для тестирования)
docker-compose -f docker-compose.server.yml up -d
docker-compose -f docker-compose.local.yml up -d
```

### Вариант 2: Продакшн (рекомендуется)
```bash
# На удаленном сервере
docker-compose -f docker-compose.server.yml up -d

# На локальной машине
docker-compose -f docker-compose.local.yml up -d
```

## 🚨 Решение проблем

### Ошибки Telegram Web App
- Убедитесь, что `WEBAPP_URL` использует HTTPS
- URL не должен содержать localhost
- Перезапустите бот после изменения `WEBAPP_URL`

### CORS ошибки  
- Добавьте все необходимые URL в `ALLOWED_ORIGINS`
- Перезапустите backend после изменения настроек

### Проблемы с портами
- Проверьте доступность портов: `lsof -i :8001`, `lsof -i :3000`
- Измените порты в `.env` при необходимости

### Ошибки подключения к БД
- Проверьте логи: `docker-compose -f docker-compose.server.yml logs db`
- Убедитесь, что база данных запущена и готова к подключениям

## 🔒 Безопасность

Для production обязательно измените:
- `SECRET_KEY` - на надежный секретный ключ
- `POSTGRES_PASSWORD` - на сильный пароль
- `ALLOWED_ORIGINS` - ограничьте конкретными доменами
- `ENVIRONMENT=production` и `LOG_LEVEL=WARNING`

Все настройки теперь централизованы в файле `.env`!