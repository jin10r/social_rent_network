# Пример развертывания Social Rent App

## Сценарий: Удаленный сервер + Локальный фронтенд через ngrok

### 1. На удаленном сервере (94.228.112.229)

```bash
# Клонирование проекта
git clone <your-repo>
cd social-rent-app

# Настройка конфигурации
cp .env.central .env

# Редактирование .env файла
BOT_TOKEN=8482163056:AAFO_l3IuliKB6I81JyQ-3_VrZuQ-8S5P-k
WEBAPP_URL=https://your-ngrok-url.ngrok-free.app
BACKEND_URL=http://94.228.112.229:8001
ALLOWED_ORIGINS=https://your-ngrok-url.ngrok-free.app

# Запуск удаленного сервера (БД + Backend + Bot)
./scripts/start-remote.sh
```

**Результат запуска:**
```
🚀 Запуск Social Rent App - Удаленный сервер
=============================================
✅ Конфигурация проверена
🛑 Остановка существующих сервисов...
🚀 Запуск сервисов...
Creating social_rent_db ... done
Creating social_rent_backend ... done  
Creating social_rent_bot ... done
⏳ Ожидание готовности сервисов...
📊 Проверка статуса сервисов:
         Name              Command            State              Ports
social_rent_backend   uvicorn main:app ...   Up      0.0.0.0:8001->8001/tcp
social_rent_bot       python main.py         Up
social_rent_db        docker-entrypoint.s..  Up      0.0.0.0:5433->5432/tcp

🏥 Проверка health checks:
✅ База данных готова
✅ Backend готов

🎉 Удаленный сервер запущен!

🌐 Доступные эндпоинты:
  Backend API: http://94.228.112.229:8001
  Backend Health: http://94.228.112.229:8001/health
  Database: 94.228.112.229:5433
```

### 2. На локальной машине разработчика

```bash
# Настройка ngrok
ngrok http 3000
# Получаем URL: https://abc123.ngrok-free.app

# Обновление конфигурации на сервере
# В .env на сервере:
WEBAPP_URL=https://abc123.ngrok-free.app
ALLOWED_ORIGINS=https://abc123.ngrok-free.app

# Перезапуск удаленного сервера с обновленной конфигурацией
ssh server "cd /path/to/app && ./scripts/start-remote.sh"

# На локальной машине - настройка .env
BACKEND_URL=http://94.228.112.229:8001
WEBAPP_URL=https://abc123.ngrok-free.app

# Запуск локального фронтенда
./scripts/start-frontend.sh
```

**Результат запуска:**
```
🚀 Запуск Social Rent App - Локальный фронтенд
===============================================
✅ Конфигурация проверена
🔍 Проверка доступности backend (http://94.228.112.229:8001)...
✅ Backend доступен
🛑 Остановка существующих сервисов...
🚀 Запуск фронтенда...
Creating social_rent_frontend ... done
⏳ Ожидание готовности фронтенда...
📊 Проверка статуса:
          Name             Command       State              Ports
social_rent_frontend   npm start       Up      0.0.0.0:3000->3000/tcp

🏥 Проверка доступности фронтенда:
✅ Фронтенд готов

🎉 Локальный фронтенд запущен!

🌐 Доступные URL:
  Локальный фронтенд: http://localhost:3000
  Backend API: http://94.228.112.229:8001
  Telegram Web App: https://abc123.ngrok-free.app
```

### 3. Проверка работы API эндпоинтов

```bash
# Проверка health check
curl http://94.228.112.229:8001/health
# Ответ: {"status":"healthy"}

# Проверка станций метро
curl http://94.228.112.229:8001/api/metro/stations
# Ответ: ["Сокольники","Красносельская","Комсомольская",...]

# Проверка объявлений
curl http://94.228.112.229:8001/api/listings/
# Ответ: [{"id":"uuid","title":"Уютная квартира","price":35000,...}]

# Создание профиля пользователя (с авторизацией)
curl -X POST http://94.228.112.229:8001/api/users/ \
  -H "Authorization: Bearer <telegram_auth_data>" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Иван",
    "age": 25,
    "bio": "Ищу квартиру в центре",
    "price_min": 30000,
    "price_max": 50000,
    "metro_station": "Тверская"
  }'
# Ответ: {"id":"uuid","telegram_id":123456789,"first_name":"Иван",...}
```

### 4. Мониторинг системы

```bash
# На удаленном сервере
./scripts/monitor.sh
```

**Вывод мониторинга:**
```
📊 Social Rent App - Мониторинг сервисов
========================================
🔍 Проверка удаленного сервера:
--------------------------------
📦 Статус контейнеров удаленного сервера:
         Name              Command            State              Ports
social_rent_backend   uvicorn main:app ...   Up      0.0.0.0:8001->8001/tcp
social_rent_bot       python main.py         Up
social_rent_db        docker-entrypoint.s..  Up      0.0.0.0:5433->5432/tcp

🏥 Health checks удаленного сервера:
✅ База данных: OK
✅ Backend API: OK (http://localhost:8001/health)
✅ Telegram Bot: OK

🔍 Проверка локального фронтенда:
---------------------------------
📦 Статус контейнера фронтенда:
          Name             Command       State              Ports
social_rent_frontend   npm start       Up      0.0.0.0:3000->3000/tcp

🏥 Health check фронтенда:
✅ Frontend: OK (http://localhost:3000)

🌐 Проверка внешних подключений:
--------------------------------
✅ Backend URL доступен: http://94.228.112.229:8001
✅ Webapp URL доступен: https://abc123.ngrok-free.app

✅ Мониторинг завершен
```

### 5. Проверка тестовых данных

```bash
# Просмотр логов backend для проверки генерации тестовых данных
./scripts/logs.sh backend
```

**Ожидаемые логи:**
```
social_rent_backend | INFO: Application startup: Initializing database...
social_rent_backend | INFO: Database tables created successfully
social_rent_backend | INFO: Application startup: Generating test data...
social_rent_backend | INFO: Starting test data generation...
social_rent_backend | INFO: Test data generation completed successfully
social_rent_backend | INFO: Application startup completed
social_rent_backend | INFO: 100 users created successfully
social_rent_backend | INFO: 1000 listings created successfully
```

## ✅ Результат

Система полностью работает:
- ✅ База данных доступна и содержит тестовые данные
- ✅ Все API эндпоинты работают корректно
- ✅ Создание/обновление профиля пользователя функционирует
- ✅ Фронтенд подключается к backend через ngrok
- ✅ Telegram бот взаимодействует с системой
- ✅ Все сервисы синхронизированы и мониторятся