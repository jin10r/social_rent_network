#!/bin/bash

# ==========================================
# СКРИПТ ПРОСМОТРА ЛОГОВ
# ==========================================
# Показывает логи сервисов

set -e

echo "📋 Social Rent App - Просмотр логов"
echo "==================================="

# Функция помощи
show_help() {
    echo "Использование: $0 [опции] [сервис]"
    echo
    echo "Опции:"
    echo "  -f, --follow     Следить за логами в реальном времени"
    echo "  -t, --tail N     Показать последние N строк (по умолчанию: 50)"
    echo "  -h, --help       Показать эту справку"
    echo
    echo "Сервисы:"
    echo "  db               Логи базы данных"
    echo "  backend          Логи backend API"
    echo "  bot              Логи Telegram бота"
    echo "  frontend         Логи React фронтенда"
    echo "  all              Логи всех сервисов (по умолчанию)"
    echo
    echo "Примеры:"
    echo "  $0 backend       Показать логи backend"
    echo "  $0 -f bot        Следить за логами бота"
    echo "  $0 -t 100 all    Показать последние 100 строк всех сервисов"
}

# Параметры по умолчанию
FOLLOW=false
TAIL=50
SERVICE="all"

# Разбор аргументов
while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--follow)
            FOLLOW=true
            shift
            ;;
        -t|--tail)
            TAIL="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        db|backend|bot|frontend|all)
            SERVICE="$1"
            shift
            ;;
        *)
            echo "❌ Неизвестный параметр: $1"
            show_help
            exit 1
            ;;
    esac
done

# Формирование команды docker-compose logs
LOGS_CMD="logs --tail=$TAIL"
if [ "$FOLLOW" = true ]; then
    LOGS_CMD="$LOGS_CMD -f"
fi

echo "📋 Просмотр логов сервиса: $SERVICE"
echo "=================================="

case $SERVICE in
    "db")
        if docker-compose -f docker-compose.remote.yml ps db | grep -q "Up"; then
            echo "🗄️  Логи базы данных:"
            docker-compose -f docker-compose.remote.yml $LOGS_CMD db
        else
            echo "❌ Сервис базы данных не запущен"
        fi
        ;;
    "backend")
        if docker-compose -f docker-compose.remote.yml ps backend | grep -q "Up"; then
            echo "🔧 Логи backend:"
            docker-compose -f docker-compose.remote.yml $LOGS_CMD backend
        else
            echo "❌ Сервис backend не запущен"
        fi
        ;;
    "bot")
        if docker-compose -f docker-compose.remote.yml ps bot | grep -q "Up"; then
            echo "🤖 Логи Telegram бота:"
            docker-compose -f docker-compose.remote.yml $LOGS_CMD bot
        else
            echo "❌ Сервис бота не запущен"
        fi
        ;;
    "frontend")
        if docker-compose -f docker-compose.frontend.yml ps frontend | grep -q "Up"; then
            echo "🎨 Логи фронтенда:"
            docker-compose -f docker-compose.frontend.yml $LOGS_CMD frontend
        else
            echo "❌ Сервис фронтенда не запущен"
        fi
        ;;
    "all")
        echo "📋 Логи всех сервисов:"
        echo
        
        # Удаленный сервер
        if docker-compose -f docker-compose.remote.yml ps | grep -q "Up"; then
            echo "🏥 === УДАЛЕННЫЙ СЕРВЕР ==="
            docker-compose -f docker-compose.remote.yml $LOGS_CMD
            echo
        fi
        
        # Фронтенд
        if docker-compose -f docker-compose.frontend.yml ps | grep -q "Up"; then
            echo "🎨 === ЛОКАЛЬНЫЙ ФРОНТЕНД ==="
            docker-compose -f docker-compose.frontend.yml $LOGS_CMD
        fi
        
        if ! docker-compose -f docker-compose.remote.yml ps | grep -q "Up" && ! docker-compose -f docker-compose.frontend.yml ps | grep -q "Up"; then
            echo "❌ Нет запущенных сервисов"
        fi
        ;;
esac

if [ "$FOLLOW" = true ]; then
    echo
    echo "👁️  Режим слежения активен. Нажмите Ctrl+C для выхода."
fi