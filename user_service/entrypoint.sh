#!/bin/sh

# Wait for the PostgreSQL database to be available
/app/wait-for-it.sh user_db:5432 -- "$@"
echo "PostgreSQL is up and running\n"
echo "Starting the migration process...\n"
alembic upgrade head
