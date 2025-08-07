# ⚙️ Руководство по настройке конфигурации

## 📝 Быстрая настройка

Все настройки приложения находятся в файле `.env`. Вам нужно изменить только эти переменные:

### 🔑 Обязательные настройки

```env
# 1. Токен вашего Telegram бота (получите у @BotFather)
BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_HERE

# 2. IP адрес вашего удаленного сервера
SERVER_IP=185.36.141.151

# 3. URL вашего ngrok туннеля для frontend (HTTPS!)
WEBAPP_URL=https://abc123.ngrok-free.app

# 4. URL для backend API (используйте IP сервера)
BACKEND_URL=http://185.36.141.151:8001

# 5. Разрешенные источники (добавьте ваш ngrok URL)
ALLOWED_ORIGINS=http://localhost:3000,https://abc123.ngrok-free.app

# 6. URL для React приложения (тот же что BACKEND_URL)
REACT_APP_BACKEND_URL=http://185.36.141.151:8001
```

## 🛠️ Пример настройки

### Шаг 1: Получение Telegram бот токена
1. Напишите @BotFather в Telegram
2. Создайте нового бота командой `/newbot`
3. Скопируйте токен (например: `123456789:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

### Шаг 2: Настройка ngrok
1. Запустите: `ngrok http 3000`
2. Скопируйте HTTPS URL (например: `https://abc123.ngrok-free.app`)

### Шаг 3: Пример готового .env файла
```env
BOT_TOKEN=123456789:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
SERVER_IP=185.36.141.151
WEBAPP_URL=https://abc123.ngrok-free.app
BACKEND_URL=http://185.36.141.151:8001
ALLOWED_ORIGINS=http://localhost:3000,https://abc123.ngrok-free.app
REACT_APP_BACKEND_URL=http://185.36.141.151:8001
REACT_APP_BOT_USERNAME=my_social_rent_bot
```

## 🚀 Запуск после настройки

```bash
# На сервере (bot + backend + db)
docker-compose -f docker-compose.server.yml up -d

# На локальной машине (frontend)  
docker-compose -f docker-compose.local.yml up -d
```

## 🔄 Изменение настроек

После изменения настроек в `.env`:

1. **Если изменили настройки бота или backend** - перезапустите сервер:
   ```bash
   docker-compose -f docker-compose.server.yml restart
   ```

2. **Если изменили frontend настройки** - перезапустите локально:
   ```bash
   docker-compose -f docker-compose.local.yml restart
   ```

## ❗ Частые ошибки

- **Не используйте HTTP для WEBAPP_URL** - только HTTPS!
- **Не забудьте добавить ngrok URL в ALLOWED_ORIGINS**
- **Проверьте, что SERVER_IP доступен с локальной машины**
- **При смене ngrok URL нужно обновить настройки и перезапустить сервер**

Готово! Теперь все настройки централизованы и легко управляемы.