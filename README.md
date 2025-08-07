# 🏠 Social Rent - Unified App

Социальная сеть для поиска жилья и соседей через Telegram Web App.
**Все сервисы объединены в один порт для простоты использования с ngrok.**

## 🚀 Быстрый запуск

### 1. Настройка конфигурации

Отредактируйте файл `.env`:

```bash
# Обязательно измените эти настройки:
BOT_TOKEN=8482163056:AAFO_l3IuliKB6I81JyQ-3_VrZuQ-8S5P-k
WEBAPP_URL=https://your-ngrok-url.ngrok-free.app  
ALLOWED_ORIGINS=https://your-ngrok-url.ngrok-free.app
POSTGRES_PASSWORD=your_secure_password_here
SECRET_KEY=your_super_secret_key_change_in_production
```

### 2. Запуск приложения

```bash
# Сборка и запуск всех сервисов
docker-compose up --build -d

# Проверка статуса
docker-compose ps

# Просмотр логов
docker-compose logs -f
```

### 3. Настройка ngrok

```bash
# В отдельном терминале
ngrok http 8001
```

Скопируйте HTTPS URL из ngrok и обновите в `.env`:
- `WEBAPP_URL=https://abc123.ngrok-free.app`
- `ALLOWED_ORIGINS=https://abc123.ngrok-free.app`

Затем перезапустите:
```bash
docker-compose restart
```

## 📋 Структура приложения

```
/app/
├── backend/         # FastAPI backend
├── frontend/        # React frontend  
├── bot/            # Telegram bot
├── static/         # Собранные файлы React (создается при сборке)
├── docker-compose.yml    # Единая конфигурация
├── Dockerfile.app       # Dockerfile для unified app
└── .env                 # Конфигурация
```

## 🌐 Порты и доступ

- **Единый порт**: 8001 (frontend + backend + API)
- **База данных**: 5432
- **Доступ к приложению**: http://localhost:8001
- **API health check**: http://localhost:8001/health
- **API endpoints**: http://localhost:8001/api/*

## 🔧 Основные команды

```bash
# Запуск
docker-compose up -d

# Пересборка
docker-compose up --build -d

# Остановка
docker-compose down

# Логи всех сервисов
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f app
docker-compose logs -f bot
docker-compose logs -f db

# Подключение к базе данных
docker-compose exec db psql -U postgres -d social_rent

# Полная очистка
docker-compose down -v
docker system prune -a
```

## ✅ Что изменилось

- ✅ **Объединены frontend и backend** в один порт 8001
- ✅ **FastAPI теперь обслуживает статические файлы** React
- ✅ **Удалены все лишние скрипты и конфигурации**
- ✅ **Один docker-compose файл** вместо нескольких
- ✅ **Упрощенная настройка ngrok** - только один туннель
- ✅ **Нет проблем с CORS** - все на одном домене

## 🛠️ Решение проблем

### Ошибки при сборке frontend
```bash
# Пересборка с очисткой кеша
docker-compose down
docker-compose build --no-cache app
docker-compose up -d
```

### Проблемы с базой данных
```bash
# Проверка подключения к БД
docker-compose exec app python -c "
from backend.database import init_database
import asyncio
asyncio.run(init_database())
"
```

### Telegram Web App не работает
1. Убедитесь что `WEBAPP_URL` использует HTTPS
2. URL должен быть доступен извне (ngrok)
3. Перезапустите бота после изменения настроек

## 📊 Тестирование

```bash
# API health check
curl http://localhost:8001/health

# Проверка frontend
curl http://localhost:8001

# Проверка API endpoint
curl http://localhost:8001/api/metro/stations
```

**Готово!** Теперь все работает через один порт с простой настройкой ngrok.