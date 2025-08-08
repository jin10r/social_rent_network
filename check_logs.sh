#!/bin/bash

echo "=== Логи nginx ==="
docker-compose logs nginx

echo "
=== Логи backend ==="
docker-compose logs backend

echo "
=== Логи frontend ==="
docker-compose logs frontend

echo "
=== Логи db ==="
docker-compose logs db

echo "
=== Логи bot ==="
docker-compose logs bot
