#!/bin/bash

# ==========================================
# СКРИПТ ОСТАНОВКИ ВСЕХ СЕРВИСОВ
# ==========================================
# Останавливает все запущенные сервисы

set -e

echo "🛑 Social Rent App - Остановка всех сервисов"
echo "============================================"

# Остановка удаленного сервера
echo "🛑 Остановка сервисов удаленного сервера..."
if docker-compose -f docker-compose.remote.yml ps | grep -q "Up"; then
    docker-compose -f docker-compose.remote.yml down
    echo "✅ Сервисы удаленного сервера остановлены"
else
    echo "ℹ️  Сервисы удаленного сервера уже остановлены"
fi

# Остановка фронтенда
echo "🛑 Остановка локального фронтенда..."
if docker-compose -f docker-compose.frontend.yml ps | grep -q "Up"; then
    docker-compose -f docker-compose.frontend.yml down
    echo "✅ Локальный фронтенд остановлен"
else
    echo "ℹ️  Локальный фронтенд уже остановлен"
fi

# Опционально - очистка volumes (с подтверждением)
echo
read -p "🗑️  Удалить данные базы данных? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️  Удаление volumes..."
    docker-compose -f docker-compose.remote.yml down -v
    echo "✅ Volumes удалены"
fi

# Опционально - очистка образов (с подтверждением)
echo
read -p "🗑️  Удалить Docker образы проекта? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️  Удаление образов..."
    docker images | grep social_rent | awk '{print $3}' | xargs -r docker rmi
    echo "✅ Образы удалены"
fi

echo
echo "✅ Все сервисы остановлены"
echo
echo "📝 Для повторного запуска используйте:"
echo "  ./scripts/start-remote.sh   # Удаленный сервер"
echo "  ./scripts/start-frontend.sh # Локальный фронтенд"