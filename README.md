# Social Rent App

Социальная сеть для поиска жилья и соседей через Telegram Web App.

## 🏗️ Архитектура

**Единый Docker Compose со всеми сервисами:**
- **nginx** - реверс-прокси для маршрутизации запросов
- **frontend** - React приложение (Telegram WebApp)  
- **backend** - FastAPI + PostgreSQL + PostGIS
- **bot** - Telegram бот (aiogram)
- **db** - PostgreSQL с расширением PostGIS

**Маршрутизация через nginx:**
- `/` - фронтенд приложение
- `/api/*` - API запросы к backend
- `/health` - проверка состояния backend

## 🚀 Быстрый запуск

### 1. Настройка ngrok URL

Измените URL в файле `.env`:

```env
WEBAPP_URL=https://your-ngrok-url.ngrok-free.app
REACT_APP_BACKEND_URL=https://your-ngrok-url.ngrok-free.app
```

### 2. Запуск приложения

```bash
# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Просмотр логов конкретного сервиса
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f nginx
docker-compose logs -f bot
docker-compose logs -f db

# Остановка
docker-compose down
```

### 3. Настройка ngrok

```bash
# Запустить ngrok для порта 80 (nginx)
ngrok http 80

# Скопировать HTTPS URL и обновить .env файл
# Перезапустить сервисы
docker-compose restart
```

## 🔧 Возможности приложения

### ✅ Реализованные функции

1. **Профиль пользователя**
   - Создание и редактирование профиля
   - Выбор станции метро с автодополнением
   - Установка бюджета и радиуса поиска

2. **Система матчинга**
   - Поиск пользователей с пересекающимися зонами поиска
   - Лайки и взаимные матчи
   - Просмотр контактов при матче

3. **Объявления недвижимости**
   - Просмотр объявлений по геолокации
   - Лайки объявлений
   - Просмотр понравившихся объявлений партнеров

4. **Тестовые данные**
   - Автоматическая генерация 1000 пользователей
   - Автоматическая генерация 1000 объявлений
   - Рандомные координаты в пределах Москвы
   - Примеры взаимодействий (лайки, матчи)

### 📊 База данных

**PostgreSQL + PostGIS с таблицами:**
- `users` - профили пользователей
- `listings` - объявления недвижимости  
- `user_likes` - лайки между пользователями
- `user_matches` - взаимные матчи
- `listing_likes` - лайки объявлений

## 🛠️ Полезные команды

### Мониторинг

```bash
# Статус сервисов
docker-compose ps

# Использование ресурсов
docker stats

# Health check
curl http://localhost/health
```

### Работа с базой данных

```bash
# Подключение к БД
docker-compose exec db psql -U postgres -d social_rent

# Просмотр данных
# SELECT COUNT(*) FROM users;
# SELECT COUNT(*) FROM listings;
# SELECT COUNT(*) FROM user_matches;
```

### Перезапуск тестовых данных

```bash
# Пересоздать и перезапустить backend для генерации новых данных
docker-compose restart backend
docker-compose logs -f backend
```

### Отладка

```bash
# Логи nginx (маршрутизация)
docker-compose logs nginx

# Логи backend (API)
docker-compose logs backend

# Логи frontend (React)
docker-compose logs frontend

# Логи бота
docker-compose logs bot
```

## 🔒 Настройки безопасности

Для production измените в `.env`:

```env
SECRET_KEY=your-strong-secret-key-here
POSTGRES_PASSWORD=strong-database-password
ENVIRONMENT=production  
LOG_LEVEL=WARNING
ALLOWED_ORIGINS=https://your-domain.com
```

## 🚨 Решение проблем

### CORS ошибки
- Убедитесь, что `REACT_APP_BACKEND_URL` правильно настроен
- nginx автоматически добавляет CORS заголовки для API

### Telegram WebApp не работает
- Убедитесь, что `WEBAPP_URL` использует HTTPS
- URL должен быть доступен извне (не localhost)
- Токен бота должен быть корректным

### Проблемы с портами
- Приложение использует только порт 80
- Все внутренние сервисы общаются через Docker сеть

### База данных не подключается
- Проверьте логи: `docker-compose logs db`
- Дождитесь полной инициализации БД (может занять 1-2 минуты)

## 📱 Использование

1. Запустите ngrok для порта 80
2. Обновите WEBAPP_URL в .env
3. Перезапустите сервисы
4. Откройте бота в Telegram (@your_bot_username)
5. Нажмите "Открыть приложение"
6. Создайте профиль и начните поиск соседей!

---

**Токен бота:** `8482163056:AAGYMcCmHUxvrzDXkBESZPGV_kGiUVHZh4I`