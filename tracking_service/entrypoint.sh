#!/bin/sh

# Wait for RabbitMQ to be available
./wait-for-it.sh rabbitmq:5672 -- echo "RabbitMQ is up and running"

# Wait for PostgreSQL database to be available
./wait-for-it.sh tracking_db:5432 -- echo "PostgreSQL is up and running"

# Run Alembic migrations
echo "Starting the migration process...\n"
alembic upgrade head

# Start the Uvicorn server
echo "Starting the Uvicorn server...\n"
exec uvicorn main:app --host 0.0.0.0 --port 8002 --reload
