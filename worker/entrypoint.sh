#!/bin/bash
# entrypoint.sh

set -e

# Esperar o RabbitMQ
echo "Waiting for RabbitMQ..."
while ! nc -z rabbitmq 5672; do
  sleep 1
done
echo "RabbitMQ is ready!"

# Esperar o banco de dados
echo "Waiting for the database..."
while ! nc -z db 5432; do
  sleep 1
done
echo "Database is ready!"

# Executar a aplicação principal
exec python consumer.py
