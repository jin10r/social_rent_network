# 🚀 Social Rent App - Деплоймент Guide

## Обзор архитектуры с Nginx Reverse Proxy

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Client    │───▶│    Nginx    │───▶│   Services  │
│ (Browser/   │    │    :8080    │    │             │
│  Telegram)  │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
                           │
                           ├─ /api/* ──▶ Backend :8001
                           ├─ /health ──▶ Backend :8001  
                           ├─ /docs ────▶ Backend :8001
                           └─ /* ──────▶ Frontend :3000
```

## 📁 Структура проекта

```
/app/
├── docker-compose.yml     # 🐳 Единый файл для всех сервисов
├── nginx.conf             # 🌐 Конфигурация reverse proxy
├── .env                   # ⚙️  Переменные окружения
├── validate-config.sh     # ✅ Проверка конфигурации
├── test-nginx-proxy.sh    # 🧪 Тестирование proxy
├── backend/               # 🔧 FastAPI приложение
├── frontend/              # 🎨 React приложение
├── bot/                   # 🤖 Telegram Bot
└── README.md             # 📚 Документация
```

## 🛠️ Быстрый деплоймент

### 1. Проверка конфигурации

```bash
# Проверить все файлы и настройки
./validate-config.sh
```

### 2. Настройка переменных окружения

Отредактируйте `.env`:

```env
# 🤖 Telegram Bot (ОБЯЗАТЕЛЬНО!)
BOT_TOKEN=your_telegram_bot_token_here
REACT_APP_BOT_USERNAME=your_bot_username_here

# 🌐 URLs (измените для продакшна)
WEBAPP_URL=http://localhost:8080
REACT_APP_BACKEND_URL=http://localhost:8080

# 🚪 Порты
NGINX_PORT=8080
```

### 3. Запуск всех сервисов

```bash
# Запустить все сервисы
docker compose up -d

# Проверить статус
docker compose ps

# Просмотр логов
docker compose logs -f
```

### 4. Тестирование

```bash
# Автоматическое тестирование proxy
./test-nginx-proxy.sh

# Ручная проверка
curl http://localhost:8080/health     # Backend
curl http://localhost:8080/           # Frontend
curl http://localhost:8080/api/metro/stations  # API
```

## 🌐 Доступ к приложению

| Сервис | URL | Описание |
|--------|-----|----------|
| **Главное приложение** | http://localhost:8080 | React фронтенд |
| **Backend API** | http://localhost:8080/api/ | FastAPI endpoints |
| **API документация** | http://localhost:8080/docs | Swagger UI |
| **Health Check** | http://localhost:8080/health | Статус backend |

## 📊 Мониторинг сервисов

### Проверка статуса

```bash
# Статус всех сервисов
docker compose ps

# Детальная информация
docker compose top
```

### Просмотр логов

```bash
# Все сервисы
docker compose logs -f

# Отдельные сервисы
docker compose logs nginx
docker compose logs backend
docker compose logs frontend
docker compose logs bot
docker compose logs db
```

### Health checks

```bash
# Backend через nginx
curl http://localhost:8080/health

# Прямая проверка сервисов (только для отладки)
curl http://localhost:8001/health     # Backend напрямую
curl http://localhost:3000/           # Frontend напрямую
```

## 🔧 Управление сервисами

### Основные команды

```bash
# Запуск
docker compose up -d

# Остановка
docker compose down

# Перезапуск
docker compose restart

# Пересборка
docker compose up --build -d

# Остановка с удалением данных
docker compose down -v
```

### Управление отдельными сервисами

```bash
# Перезапуск nginx после изменения конфигурации
docker compose restart nginx

# Перезапуск backend после изменения кода
docker compose restart backend

# Просмотр логов конкретного сервиса
docker compose logs -f backend
```

## 🌍 Настройка для продакшна

### 1. HTTPS с ngrok (для разработки)

```bash
# Установите ngrok
ngrok http 8080

# Обновите .env
WEBAPP_URL=https://abc123.ngrok-free.app
REACT_APP_BACKEND_URL=https://abc123.ngrok-free.app
ALLOWED_ORIGINS=https://abc123.ngrok-free.app,http://localhost:8080
```

### 2. Продакшн сервер

```bash
# 1. Клонируйте проект
git clone <your-repo>
cd social-rent-app

# 2. Настройте .env для продакшна
ENVIRONMENT=production
WEBAPP_URL=https://yourdomain.com
REACT_APP_BACKEND_URL=https://yourdomain.com
SECRET_KEY=your_super_secret_key_here
POSTGRES_PASSWORD=strong_password_here
LOG_LEVEL=WARNING

# 3. Запустите с продакшн настройками
docker compose up -d
```

## 🚨 Устранение проблем

### Nginx не запускается

```bash
# Проверьте конфигурацию
docker compose config

# Проверьте логи nginx
docker compose logs nginx

# Проверьте синтаксис nginx.conf
docker run --rm -v $(pwd)/nginx.conf:/etc/nginx/conf.d/default.conf nginx nginx -t
```

### Backend недоступен

```bash
# Проверьте что backend запущен
docker compose ps backend

# Логи backend
docker compose logs backend

# Проверьте подключение к БД
docker compose exec backend python -c "from database import get_database; print('DB OK')"
```

### Frontend не загружается

```bash
# Логи frontend
docker compose logs frontend

# Проверьте сборку
docker compose exec frontend npm run build

# Перезапуск frontend
docker compose restart frontend
```

### База данных недоступна

```bash
# Статус БД
docker compose ps db

# Логи БД
docker compose logs db

# Подключение к БД
docker compose exec db psql -U postgres -d social_rent
```

## 🔒 Безопасность

### Обязательно измените для продакшна:

- [ ] `BOT_TOKEN` - реальный токен от @BotFather
- [ ] `SECRET_KEY` - случайный ключ (используйте генератор)
- [ ] `POSTGRES_PASSWORD` - сильный пароль
- [ ] `ALLOWED_ORIGINS` - конкретные домены
- [ ] `ENVIRONMENT=production`
- [ ] Используйте HTTPS для всех внешних URL

### Рекомендуемые настройки:

```env
# Продакшн безопасность
ENVIRONMENT=production
LOG_LEVEL=WARNING
SECRET_KEY=randomly_generated_secret_key_32_chars_long
POSTGRES_PASSWORD=StrongPassword123!
ALLOWED_ORIGINS=https://yourdomain.com
```

## 📈 Масштабирование

### Горизонтальное масштабирование

Для увеличения нагрузки можно добавить multiple instances:

```yaml
# В docker-compose.yml
backend:
  # ...
  deploy:
    replicas: 3

frontend:
  # ...  
  deploy:
    replicas: 2
```

### Мониторинг производительности

```bash
# Использование ресурсов
docker compose top

# Статистика контейнеров
docker stats

# Логи с временными метками
docker compose logs -f -t
```

## ✅ Чеклист деплоя

- [ ] Проверена конфигурация (`./validate-config.sh`)
- [ ] Настроены переменные окружения в `.env`
- [ ] Установлен реальный `BOT_TOKEN`
- [ ] Настроен `WEBAPP_URL` для внешнего доступа
- [ ] Запущены все сервисы (`docker compose up -d`)
- [ ] Протестированы endpoints (`./test-nginx-proxy.sh`)
- [ ] Проверены логи всех сервисов
- [ ] Настроен мониторинг
- [ ] Настроена безопасность для продакшна

---

**🎉 Приложение готово к использованию!**

Nginx успешно проксирует все запросы между фронтендом и бекендом через единую точку входа на порту 8080.