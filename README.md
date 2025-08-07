# 🏠 Social Rent - Unified App

Социальная сеть для поиска жилья и соседей через Telegram Web App.
**Frontend и Backend объединены в один порт для простой работы с ngrok!**

## ✅ Что готово

- ✅ **Backend** (FastAPI): порт 8001 - API + статические файлы React
- ✅ **Frontend** (React): собран и интегрирован в backend
- ✅ **Telegram Bot**: готов к работе с ngrok
- ✅ **Database** (PostgreSQL + PostGIS): полностью настроена
- ✅ **Удалены лишние файлы**: только необходимое для функционала

## 🚀 Быстрый запуск

### 1. Проверка текущего статуса

```bash
# Проверить статус сервисов
supervisorctl status

# Если нужно - перезапустить все сервисы
supervisorctl restart all
```

### 2. Настройка ngrok

```bash
# В отдельном терминале запустите ngrok для порта 8001
ngrok http 8001
```

**Важно**: Теперь нужно настроить только один туннель на порт 8001!

### 3. Обновление конфигурации

Отредактируйте файл `/app/.env` и укажите ваш ngrok URL:

```env
# Замените на ваш ngrok URL
WEBAPP_URL=https://abc123.ngrok-free.app
ALLOWED_ORIGINS=https://abc123.ngrok-free.app
```

Затем перезапустите сервисы:
```bash
supervisorctl restart all
```

## 🌐 Доступ к приложению

После настройки ngrok у вас будут доступны:

- **🌐 Веб-приложение**: `https://your-ngrok-url.ngrok-free.app`
- **📱 API**: `https://your-ngrok-url.ngrok-free.app/api/*`
- **🏥 Health Check**: `https://your-ngrok-url.ngrok-free.app/health`
- **📖 API Docs**: `https://your-ngrok-url.ngrok-free.app/docs`

**Локальный доступ (для разработки)**:
- **🌐 Приложение**: `http://localhost:8001`
- **📱 API**: `http://localhost:8001/api/*` 
- **🏥 Health Check**: `http://localhost:8001/health`

## 🔧 Основные команды

```bash
# Статус сервисов
supervisorctl status

# Перезапуск всех сервисов
supervisorctl restart all

# Перезапуск отдельного сервиса
supervisorctl restart backend
supervisorctl restart bot

# Логи сервисов
tail -f /var/log/supervisor/backend.log
tail -f /var/log/supervisor/bot.log

# Подключение к базе данных
sudo -u postgres psql -d social_rent
```

## 🛠️ Структура приложения

```
/app/
├── backend/                 # FastAPI backend
│   ├── main.py             # Основной файл с API + статическими файлами
│   ├── models.py           # Модели базы данных
│   ├── services.py         # Бизнес логика
│   └── ...
├── frontend/               # React frontend (исходники)
│   ├── src/
│   └── build/             # Собранные файлы
├── static/                # Статические файлы для backend (копия build/)
├── bot/                   # Telegram bot
└── .env                   # Конфигурация
```

## 📊 Пример настройки .env

```env
# ЕДИНЫЙ ПОРТ ДЛЯ ВСЕГО
APP_PORT=8001

# TELEGRAM BOT (ОБЯЗАТЕЛЬНО ИЗМЕНИТЬ!)
BOT_TOKEN=your_bot_token_from_botfather
WEBAPP_URL=https://your-ngrok-url.ngrok-free.app
BOT_USERNAME=your_bot_username

# БЕЗОПАСНОСТЬ
ALLOWED_ORIGINS=https://your-ngrok-url.ngrok-free.app
SECRET_KEY=your_super_secret_key

# DATABASE (уже настроено)
DATABASE_URL=postgresql+asyncpg://postgres:postgres123@localhost:5432/social_rent
```

## 🔍 Тестирование

```bash
# Health check
curl http://localhost:8001/health

# Frontend (должен вернуть HTML)
curl http://localhost:8001/

# API endpoint
curl http://localhost:8001/api/metro/stations

# API документация
curl http://localhost:8001/docs
```

## 🛠️ Решение проблем

### Backend не запускается
```bash
# Проверить логи
tail -n 50 /var/log/supervisor/backend.log

# Проверить базу данных
sudo -u postgres psql -d social_rent -c "SELECT version();"

# Перезапустить PostgreSQL если нужно
service postgresql restart
```

### Bot не работает
```bash
# Проверить логи
tail -n 50 /var/log/supervisor/bot.log

# Убедиться что WEBAPP_URL правильный в .env
# Перезапустить бота
supervisorctl restart bot
```

### Frontend не обновляется
```bash
# Пересобрать frontend
cd /app/frontend && yarn build

# Скопировать в статическую папку
cp -r /app/frontend/build/* /app/static/

# Перезапустить backend
supervisorctl restart backend
```

## 🎉 Готово!

Теперь ваше приложение работает через **один порт 8001**, что решает проблему с ngrok! 

- **Frontend и Backend** объединены
- **Нет проблем с CORS**
- **Простая настройка ngrok**: только один туннель
- **Все данные доступны из БД**

**Запустите `ngrok http 8001`, обновите WEBAPP_URL в .env и все готово к работе!**