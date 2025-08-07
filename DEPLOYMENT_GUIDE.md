# 🚀 Руководство по развертыванию Social Rent App

Пошаговое руководство по развертыванию приложения на двух машинах.

## 📋 Архитектура развертывания

- **Удаленный сервер**: База данных + Backend API + Telegram Bot
- **Локальная машина**: Frontend приложение (через ngrok для внешнего доступа)

## 🔧 Предварительные требования

- Docker и Docker Compose установлены на обеих машинах
- Доступ к удаленному серверу по SSH
- Ngrok аккаунт для внешнего доступа к frontend
- Telegram бот токен от @BotFather

## 🌍 Шаг 1: Настройка удаленного сервера

### 1.1 Подготовка сервера

```bash
# Подключитесь к удаленному серверу
ssh user@YOUR_SERVER_IP

# Установите Docker (если не установлен)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Установите Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 1.2 Копирование проекта

```bash
# Скопируйте проект на сервер
scp -r /path/to/social-rent-app user@YOUR_SERVER_IP:/home/user/social-rent-app

# Или используйте git
git clone YOUR_REPOSITORY_URL /home/user/social-rent-app
```

### 1.3 Настройка конфигурации

```bash
cd /home/user/social-rent-app

# Отредактируйте .env файл
nano .env
```

**Основные настройки для сервера:**
```env
# Замените на ваши значения
BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_FROM_BOTFATHER
SERVER_IP=YOUR_ACTUAL_SERVER_IP
WEBAPP_URL=https://YOUR_NGROK_URL.ngrok-free.app
BACKEND_URL=http://YOUR_ACTUAL_SERVER_IP:8001
ALLOWED_ORIGINS=http://localhost:3000,https://YOUR_NGROK_URL.ngrok-free.app

# Настройки базы данных (можете оставить как есть)
POSTGRES_PASSWORD=CHANGE_THIS_IN_PRODUCTION
DB_EXTERNAL_PORT=5432
```

### 1.4 Запуск сервисов на сервере

```bash
# Запуск всех серверных сервисов
docker-compose -f docker-compose.server.yml --env-file .env up -d

# Проверка статуса
docker-compose -f docker-compose.server.yml ps

# Просмотр логов
docker-compose -f docker-compose.server.yml logs -f
```

### 1.5 Проверка работы сервера

```bash
# Проверка backend API
curl http://YOUR_SERVER_IP:8001/health

# Проверка документации API
curl http://YOUR_SERVER_IP:8001/docs

# Проверка базы данных
docker exec -it social_rent_db psql -U postgres -d social_rent -c "\dt"
```

## 💻 Шаг 2: Настройка локальной машины

### 2.1 Подготовка локального окружения

```bash
# Перейдите в директорию проекта на локальной машине
cd /path/to/social-rent-app

# Убедитесь, что Docker запущен
docker --version
docker-compose --version
```

### 2.2 Настройка локальной конфигурации  

Отредактируйте `.env` файл для локального использования:

```env
# Backend подключение к удаленному серверу
REACT_APP_BACKEND_URL=http://YOUR_SERVER_IP:8001
REACT_APP_BOT_USERNAME=your_bot_username

# Frontend настройки
FRONTEND_PORT=3000
```

### 2.3 Настройка Ngrok

```bash
# Установите ngrok (если не установлен)
# Для Ubuntu/Debian:
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok

# Для macOS:
brew install ngrok/ngrok/ngrok

# Авторизуйтесь в ngrok (получите токен на https://ngrok.com)
ngrok config add-authtoken YOUR_NGROK_AUTH_TOKEN
```

### 2.4 Запуск локального frontend

```bash
# Запуск frontend
docker-compose -f docker-compose.local.yml --env-file .env up -d

# Проверка статуса
docker-compose -f docker-compose.local.yml ps

# Просмотр логов
docker-compose -f docker-compose.local.yml logs -f frontend
```

### 2.5 Настройка Ngrok туннеля

```bash
# В новом терминале запустите ngrok
ngrok http 3000

# Скопируйте HTTPS URL из вывода (например: https://abc123.ngrok-free.app)
```

**Важно**: Обновите настройки на сервере с новым ngrok URL:

```bash
# На сервере обновите .env
WEBAPP_URL=https://abc123.ngrok-free.app
ALLOWED_ORIGINS=http://localhost:3000,https://abc123.ngrok-free.app

# Перезапустите сервисы
docker-compose -f docker-compose.server.yml restart backend bot
```

## ✅ Шаг 3: Проверка развертывания

### 3.1 Тестирование подключений

```bash
# Проверка backend API с локальной машины
curl http://YOUR_SERVER_IP:8001/health

# Проверка frontend
curl http://localhost:3000

# Проверка ngrok URL
curl https://your-ngrok-url.ngrok-free.app
```

### 3.2 Тестирование Telegram бота

1. Найдите вашего бота в Telegram
2. Отправьте команду `/start`
3. Нажмите кнопку "🏠 Открыть приложение"
4. Убедитесь, что веб-приложение открывается

### 3.3 Проверка интеграции

1. Зарегистрируйтесь в веб-приложении
2. Создайте профиль пользователя
3. Проверьте, что данные сохраняются в базе данных на сервере

## 🔄 Управление сервисами

### Команды для сервера

```bash
# Перезапуск всех сервисов
docker-compose -f docker-compose.server.yml restart

# Перезапуск конкретного сервиса
docker-compose -f docker-compose.server.yml restart backend
docker-compose -f docker-compose.server.yml restart bot

# Остановка
docker-compose -f docker-compose.server.yml down

# Полная остановка с удалением данных
docker-compose -f docker-compose.server.yml down -v
```

### Команды для локальной машины

```bash
# Перезапуск frontend
docker-compose -f docker-compose.local.yml restart

# Остановка
docker-compose -f docker-compose.local.yml down

# Просмотр логов
docker-compose -f docker-compose.local.yml logs -f
```

## 🛠️ Обслуживание и мониторинг

### Проверка здоровья сервисов

```bash
# Проверка всех health checks
docker-compose -f docker-compose.server.yml ps

# Детальная проверка
curl http://YOUR_SERVER_IP:8001/health
curl http://localhost:3000
```

### Резервное копирование базы данных

```bash
# Создание бэкапа
docker exec social_rent_db pg_dump -U postgres social_rent > backup_$(date +%Y%m%d_%H%M%S).sql

# Восстановление из бэкапа
docker exec -i social_rent_db psql -U postgres social_rent < backup.sql
```

### Обновление приложения

```bash
# На сервере
git pull origin main
docker-compose -f docker-compose.server.yml build --no-cache
docker-compose -f docker-compose.server.yml up -d

# На локальной машине  
git pull origin main
docker-compose -f docker-compose.local.yml build --no-cache
docker-compose -f docker-compose.local.yml up -d
```

## 🚨 Устранение неполадок

### Проблемы с подключением

1. **Frontend не может подключиться к backend:**
   - Проверьте настройку `REACT_APP_BACKEND_URL`
   - Убедитесь, что порт 8001 открыт на сервере
   - Проверьте firewall настройки

2. **CORS ошибки:**
   - Обновите `ALLOWED_ORIGINS` на сервере
   - Перезапустите backend после изменений

3. **Telegram Web App не открывается:**
   - Убедитесь, что используете HTTPS URL
   - Проверьте настройку `WEBAPP_URL`
   - URL не должен содержать localhost

### Проблемы с базой данных

```bash
# Проверка подключения к БД
docker exec social_rent_db pg_isready -U postgres

# Проверка логов БД
docker-compose -f docker-compose.server.yml logs db

# Перезапуск БД
docker-compose -f docker-compose.server.yml restart db
```

### Проблемы с Ngrok

1. **Ngrok URL не работает:**
   - Проверьте, что ngrok все еще активен
   - Обновите URL в настройках сервера
   - Используйте платную подписку ngrok для стабильности

2. **Частая смена URL:**
   - Используйте зарезервированные домены в ngrok
   - Настройте автоматическое обновление конфигурации

## 🔒 Безопасность в продакшн

1. **Измените пароли по умолчанию:**
   ```env
   POSTGRES_PASSWORD=STRONG_SECURE_PASSWORD
   SECRET_KEY=LONG_RANDOM_SECRET_KEY
   ```

2. **Ограничьте доступ:**
   ```env
   ALLOWED_ORIGINS=https://your-secure-domain.com
   ```

3. **Настройте SSL/TLS для backend**

4. **Настройте firewall правила**

5. **Регулярные обновления и бэкапы**

Развертывание завершено! Ваше приложение теперь работает на двух машинах с централизованными настройками.