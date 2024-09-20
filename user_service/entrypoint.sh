#!/bin/sh

# Wait for the PostgreSQL database to be available
/app/wait-for-it.sh user_db:5432 -- "$@"

echo "PostgreSQL is up and running\n"

# Run Alembic migrations
echo "Starting the migration process...\n"
alembic upgrade head

# Start the Uvicorn server
echo "Starting the Uvicorn server...\n"
exec uvicorn main:app --host 0.0.0.0 --port 8001 --reload

