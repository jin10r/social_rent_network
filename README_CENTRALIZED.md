# Social Rent App - Централизованная конфигурация

🏠 **Социальная сеть для поиска жилья и соседей через Telegram Web App**

## 🚀 Быстрый старт

### 1. Настройка конфигурации
```bash
# Автоматическая настройка
./scripts/setup-config.sh

# Или вручную
cp .env.central .env
# Отредактируйте .env файл
```

### 2. Запуск сервисов

#### Вариант A: Удаленный сервер (bot + backend + database)
```bash
./scripts/start-remote.sh
```

#### Вариант B: Локальный фронтенд (подключается к удаленному backend)
```bash  
./scripts/start-frontend.sh
```

## 📁 Структура проекта

```
/app/
├── 🔧 Конфигурация
│   ├── .env.central              # Шаблон централизованной конфигурации
│   ├── .env                      # Ваш рабочий файл конфигурации
│   ├── docker-compose.remote.yml # Удаленный сервер (bot+backend+db)
│   └── docker-compose.frontend.yml # Локальный фронтенд
│
├── 🚀 Компоненты приложения
│   ├── backend/                  # FastAPI backend
│   ├── frontend/                 # React frontend
│   ├── bot/                      # Telegram bot (aiogram)
│   └── scripts/                  # Скрипты управления
│
└── 📚 Документация
    ├── README_CENTRALIZED.md     # Это руководство
    ├── CENTRALIZED_CONFIG_GUIDE.md # Подробное руководство
    └── DOCKER_COMPOSE_GUIDE.md   # Старое руководство
```

## 🛠️ Управление сервисами

### Основные команды

```bash
# 🚀 Запуск
./scripts/start-remote.sh       # Удаленный сервер
./scripts/start-frontend.sh     # Локальный фронтенд

# 📊 Мониторинг
./scripts/monitor.sh            # Статус всех сервисов

# 📋 Логи
./scripts/logs.sh               # Все логи
./scripts/logs.sh backend       # Логи конкретного сервиса
./scripts/logs.sh -f bot        # Следить за логами бота

# 🛑 Остановка
./scripts/stop-all.sh           # Остановить все сервисы
```

### Docker Compose команды

```bash
# Удаленный сервер
docker-compose -f docker-compose.remote.yml --env-file .env up -d
docker-compose -f docker-compose.remote.yml down

# Локальный фронтенд
docker-compose -f docker-compose.frontend.yml --env-file .env up -d
docker-compose -f docker-compose.frontend.yml down
```

## ⚙️ Настройка переменных окружения

### Обязательные переменные в `.env`:

```env
# Telegram бот
BOT_TOKEN=your_telegram_bot_token
BOT_USERNAME=your_bot_username

# Публичные URL (HTTPS для Telegram)
WEBAPP_URL=https://your-ngrok-url.ngrok-free.app
BACKEND_URL=http://your-server-ip:8001

# CORS
ALLOWED_ORIGINS=https://your-ngrok-url.ngrok-free.app,http://localhost:3000
```

## 🌐 Сценарии развертывания

### Сценарий 1: Полная локальная разработка
```bash
# 1. Настройте .env для локальной работы
BACKEND_URL=http://localhost:8001
WEBAPP_URL=https://12345.ngrok-free.app

# 2. Запустите все сервисы
./scripts/start-remote.sh    # backend + db + bot
./scripts/start-frontend.sh  # frontend

# 3. Настройте ngrok
ngrok http 3000
```

### Сценарий 2: Удаленный backend + локальный frontend
```bash
# На удаленном сервере:
./scripts/start-remote.sh

# На локальной машине:  
# Настройте .env с URL удаленного сервера
BACKEND_URL=http://your-server-ip:8001
./scripts/start-frontend.sh
```

## 🔍 Мониторинг и отладка

### Проверка статуса сервисов
```bash
./scripts/monitor.sh
```

### Просмотр логов
```bash
./scripts/logs.sh              # Все логи
./scripts/logs.sh -f backend   # Следить за backend
./scripts/logs.sh -t 100 bot   # Последние 100 строк бота
```

### Health checks
```bash
# Backend
curl http://localhost:8001/health

# Frontend  
curl http://localhost:3000

# Database
docker-compose -f docker-compose.remote.yml exec db pg_isready -U postgres -d social_rent
```

## 🌍 Настройка с ngrok

### Ручная настройка
```bash
# 1. Запустите ngrok
ngrok http 3000

# 2. Скопируйте HTTPS URL (например: https://12345.ngrok-free.app)

# 3. Обновите .env
WEBAPP_URL=https://12345.ngrok-free.app
ALLOWED_ORIGINS=https://12345.ngrok-free.app,http://localhost:3000

# 4. Перезапустите сервисы
./scripts/start-remote.sh
```

## 🐛 Решение проблем

### Порт уже используется
```bash
# Найти процесс
lsof -i :8001
lsof -i :3000

# Изменить порты в .env
BACKEND_PORT=8002
FRONTEND_PORT=3001
```

### Ошибки подключения к БД
```bash
# Проверить логи
./scripts/logs.sh db

# Проверить подключение
docker exec -it social_rent_db psql -U postgres -d social_rent
```

### Telegram Web App URL is invalid
1. Убедитесь, что используете HTTPS URL
2. URL не должен содержать localhost
3. Проверьте WEBAPP_URL в .env
4. Перезапустите бот

## 📊 Полезные команды

### Генерация тестовых данных
```bash
docker-compose -f docker-compose.remote.yml run --rm test-data-generator python generate_test_data.py
```

### Пересборка контейнеров
```bash
./scripts/start-remote.sh --build
./scripts/start-frontend.sh --build
```

### Очистка системы
```bash
./scripts/stop-all.sh
docker system prune -a
```

## 🔒 Production настройки

### Безопасность
```env
SECRET_KEY=your_very_secure_secret_key
POSTGRES_PASSWORD=secure_database_password
ENVIRONMENT=production
LOG_LEVEL=WARNING
```

### CORS
```env
# Ограничьте источники конкретными доменами
ALLOWED_ORIGINS=https://your-domain.com,https://your-app.ngrok-free.app
```

## 💡 Преимущества новой системы

✅ **Централизованная конфигурация** - все настройки в одном месте  
✅ **Простые скрипты** - автоматизация рутинных задач  
✅ **Гибкое развертывание** - разные сценарии для разных нужд  
✅ **Health checks** - надежность и мониторинг  
✅ **Подробная документация** - легко разобраться  
✅ **Синхронизация сервисов** - правильные зависимости  

## 📞 Поддержка

При проблемах:
1. Проверьте `./scripts/monitor.sh`
2. Посмотрите логи `./scripts/logs.sh`
3. Убедитесь что все переменные в `.env` заданы корректно
4. Проверьте доступность портов

---

🎉 **Все настройки теперь централизованы и легко управляемы!**