# 🚀 Быстрый старт Social Rent App

## 📁 Что было сделано

✅ **Централизованы все настройки** в единый файл `.env`  
✅ **Создано 2 docker-compose файла**:
- `docker-compose.server.yml` - для сервера (bot + backend + database)
- `docker-compose.local.yml` - для локальной машины (frontend)  
✅ **Удалены лишние docker-compose файлы**  
✅ **Логика приложения не изменена**  
✅ **Проект готов к деплою**

## ⚡ Быстрая настройка (30 секунд)

### 1. Автоматическая настройка
```bash
./scripts/setup-config.sh
```
Интерактивный помощник поможет настроить все переменные.

### 2. Ручная настройка  
Отредактируйте `.env` файл:
```bash
nano .env
```
Измените эти значения:
- `BOT_TOKEN` - токен от @BotFather
- `SERVER_IP` - IP вашего сервера  
- `WEBAPP_URL` - ваш ngrok URL
- `BACKEND_URL` - http://ВАШ_IP:8001
- `ALLOWED_ORIGINS` - добавьте ваш ngrok URL

## 🚀 Запуск (2 команды)

### На удаленном сервере:
```bash
./scripts/server-start.sh
```

### На локальной машине:
```bash  
./scripts/local-start.sh
```

## 🎯 Доступные скрипты

| Скрипт | Описание |
|--------|----------|
| `./scripts/setup-config.sh` | 🔧 Интерактивная настройка конфигурации |
| `./scripts/server-start.sh` | 🚀 Запуск сервера (bot+backend+db) |
| `./scripts/local-start.sh` | 💻 Запуск локального frontend |
| `./scripts/server-restart.sh` | 🔄 Перезапуск сервисов на сервере |
| `./scripts/show-status.sh` | 📊 Показать статус всех сервисов |
| `./scripts/stop-all.sh` | 🛑 Остановить все сервисы |

## 📚 Документация

| Файл | Описание |
|------|----------|
| `CONFIG_GUIDE.md` | 📝 Краткий гайд по настройке |
| `DEPLOYMENT_GUIDE.md` | 🚀 Полное руководство по развертыванию |  
| `README.md` | 📖 Основная документация проекта |

## 🔗 Проверка работы

После запуска проверьте:
- 🌐 Backend: `http://ВАШ_IP:8001/health`
- 💻 Frontend: `http://localhost:3000`  
- 🔗 Ngrok: `https://ваш-url.ngrok-free.app`
- 🤖 Telegram бот: найдите в Telegram и отправьте `/start`

## 💡 Быстрые команды

```bash
# Настройка одной командой
./scripts/setup-config.sh

# Запуск на сервере  
./scripts/server-start.sh

# Запуск локально
./scripts/local-start.sh  

# Проверка статуса
./scripts/show-status.sh

# Просмотр логов сервера
docker-compose -f docker-compose.server.yml logs -f

# Просмотр логов frontend
docker-compose -f docker-compose.local.yml logs -f
```

## 🛠️ Все готово к деплою!

Проект полностью настроен для работы на двух машинах с централизованной конфигурацией. Просто укажите ваши настройки в `.env` файле и запускайте!