#!/bin/bash

# Остановка всех контейнеров
echo "Остановка контейнеров..."
docker-compose down

# Удаление volume базы данных
echo "Удаление volume базы данных..."
docker volume rm social_rent_postgres_data || true

# Пересоздание volume и запуск контейнеров
echo "Пересоздание volume и запуск контейнеров..."
./start.sh

echo "
Проверка статуса контейнеров..."
docker-compose ps

echo "
Готово! Приложение должно быть доступно по адресу http://localhost через несколько секунд."
