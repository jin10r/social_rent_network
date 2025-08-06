# Руководство по централизованной конфигурации Social Rent App

## 📋 Обзор

Все настройки приложения теперь централизованы в единой конфигурации. Это руководство объясняет, как использовать новую систему конфигурации.

## 🗂️ Структура файлов конфигурации

```
/app/
├── .env.central          # Шаблон централизованной конфигурации
├── .env                  # Ваш рабочий файл конфигурации (создайте из .env.central)
├── docker-compose.remote.yml     # Для удаленного сервера (bot + backend + db)  
├── docker-compose.frontend.yml   # Для локального фронтенда через ngrok
└── CENTRALIZED_CONFIG_GUIDE.md   # Это руководство
```

## 🚀 Быстрый старт

### Шаг 1: Настройка конфигурации

```bash
# Скопируйте шаблон конфигурации
cp .env.central .env

# Отредактируйте .env файл под ваши нужды
nano .env
```

### Шаг 2A: Запуск удаленного сервера (bot + backend + database)

```bash
# На удаленном сервере
docker-compose -f docker-compose.remote.yml --env-file .env up -d

# Просмотр логов
docker-compose -f docker-compose.remote.yml logs -f

# Остановка сервисов
docker-compose -f docker-compose.remote.yml down
```

### Шаг 2B: Запуск локального фронтенда

```bash
# На локальной машине (фронтенд подключается к удаленному backend)
docker-compose -f docker-compose.frontend.yml --env-file .env up -d

# Просмотр логов фронтенда
docker-compose -f docker-compose.frontend.yml logs -f frontend
```

## ⚙️ Настройка переменных окружения

### Основные переменные для редактирования в `.env`:

```env
# 1. Токен Telegram бота (получить у @BotFather)
BOT_TOKEN=your_telegram_bot_token_here

# 2. URL для веб-приложения (HTTPS обязательно для Telegram)
WEBAPP_URL=https://your-ngrok-frontend-url.ngrok-free.app

# 3. URL для backend API
BACKEND_URL=http://your-server-ip:8001

# 4. Разрешенные источники для CORS
ALLOWED_ORIGINS=https://your-ngrok-frontend-url.ngrok-free.app,http://localhost:3000

# 5. Имя пользователя бота (без @)
BOT_USERNAME=your_bot_username
```

## 🌐 Настройка с ngrok

### Вариант 1: Ручная настройка ngrok

```bash
# 1. Установите ngrok: https://ngrok.com/download

# 2. Запустите ngrok для фронтенда
ngrok http 3000

# 3. Скопируйте HTTPS URL из вывода ngrok (например: https://12345.ngrok-free.app)

# 4. Обновите переменные в .env:
WEBAPP_URL=https://12345.ngrok-free.app
ALLOWED_ORIGINS=https://12345.ngrok-free.app,http://localhost:3000

# 5. Перезапустите сервисы
docker-compose -f docker-compose.remote.yml --env-file .env restart
```

### Вариант 2: Автоматический ngrok (опционально)

```bash
# 1. Получите токен на ngrok.com
# 2. Добавьте в .env:
NGROK_AUTHTOKEN=your_ngrok_auth_token

# 3. Раскомментируйте ngrok сервис в docker-compose.frontend.yml
# 4. Запустите:
docker-compose -f docker-compose.frontend.yml up -d
```

## 📊 Мониторинг сервисов

### Проверка статуса всех сервисов:

```bash
# Удаленный сервер
docker-compose -f docker-compose.remote.yml ps

# Локальный фронтенд  
docker-compose -f docker-compose.frontend.yml ps
```

### Проверка здоровья сервисов:

```bash
# Health check базы данных
curl http://localhost:5433  # или ваш DB_EXTERNAL_PORT

# Health check backend
curl http://localhost:8001/health

# Health check frontend
curl http://localhost:3000
```

### Просмотр логов:

```bash
# Все сервисы удаленного сервера
docker-compose -f docker-compose.remote.yml logs -f

# Конкретный сервис
docker-compose -f docker-compose.remote.yml logs -f backend
docker-compose -f docker-compose.remote.yml logs -f bot

# Фронтенд
docker-compose -f docker-compose.frontend.yml logs -f frontend
```

## 🎯 Сценарии развертывания

### Сценарий 1: Полная локальная разработка

```env
# В .env файле:
BOT_TOKEN=your_test_bot_token
WEBAPP_URL=https://12345.ngrok-free.app
BACKEND_URL=http://localhost:8001
ALLOWED_ORIGINS=http://localhost:3000,https://12345.ngrok-free.app
```

```bash
# Запуск всех сервисов локально
docker-compose -f docker-compose.remote.yml up -d
docker-compose -f docker-compose.frontend.yml up -d
```

### Сценарий 2: Удаленный backend, локальный frontend

```env
# В .env файле:
BOT_TOKEN=your_real_bot_token
WEBAPP_URL=https://your-ngrok-url.ngrok-free.app  
BACKEND_URL=http://your-server-ip:8001
ALLOWED_ORIGINS=https://your-ngrok-url.ngrok-free.app
```

```bash
# На удаленном сервере:
docker-compose -f docker-compose.remote.yml up -d

# На локальной машине:
docker-compose -f docker-compose.frontend.yml up -d
```

### Сценарий 3: Полное production развертывание

```env
# В .env файле:
ENVIRONMENT=production
BOT_TOKEN=your_production_bot_token
WEBAPP_URL=https://your-domain.com
BACKEND_URL=https://api.your-domain.com
ALLOWED_ORIGINS=https://your-domain.com
```

## 🛠️ Полезные команды

### Генерация тестовых данных:

```bash
# Ручная генерация тестовых данных
docker-compose -f docker-compose.remote.yml run --rm test-data-generator python generate_test_data.py
```

### Пересборка контейнеров:

```bash
# Пересборка с очисткой кэша
docker-compose -f docker-compose.remote.yml build --no-cache
docker-compose -f docker-compose.frontend.yml build --no-cache
```

### Очистка системы:

```bash
# Остановка и удаление всех контейнеров
docker-compose -f docker-compose.remote.yml down -v
docker-compose -f docker-compose.frontend.yml down -v

# Очистка неиспользуемых образов
docker system prune -a
```

## 🚨 Решение проблем

### Проблема: Порт уже используется

```bash
# Найти процесс, использующий порт
lsof -i :8001
lsof -i :3000
lsof -i :5433

# Изменить порты в .env файле
BACKEND_PORT=8002
FRONTEND_PORT=3001
DB_EXTERNAL_PORT=5434
```

### Проблема: Ошибка подключения к базе данных

```bash
# Проверить логи базы данных
docker-compose -f docker-compose.remote.yml logs db

# Проверить подключение вручную
docker exec -it social_rent_db psql -U postgres -d social_rent
```

### Проблема: Telegram Web App URL is invalid

1. Убедитесь, что используете HTTPS URL
2. URL не должен содержать localhost
3. Проверьте, что WEBAPP_URL корректно установлен в .env
4. Перезапустите бот после изменения конфигурации

### Проблема: CORS ошибки

```env
# Добавьте все необходимые источники в ALLOWED_ORIGINS
ALLOWED_ORIGINS=http://localhost:3000,https://your-ngrok-url.ngrok-free.app,https://your-domain.com
```

## 🔒 Безопасность

### Production настройки:

1. Измените `SECRET_KEY` на надежный ключ
2. Используйте сильные пароли для базы данных
3. Ограничьте `ALLOWED_ORIGINS` конкретными доменами
4. Используйте HTTPS везде где возможно

### Переменные для production:

```env
SECRET_KEY=your_very_secure_secret_key_here
POSTGRES_PASSWORD=your_secure_database_password
ENVIRONMENT=production
LOG_LEVEL=WARNING
```

## 📞 Поддержка

Если возникли проблемы:

1. Проверьте логи сервисов
2. Убедитесь, что все переменные в .env корректно заданы  
3. Проверьте health checks сервисов
4. Проверьте доступность портов

Все настройки теперь централизованы и легко управляемы!