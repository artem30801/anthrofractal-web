#!/bin/bash

echo "Waiting for PostgreSQL..."

# shellcheck disable=SC2034
for run in {1..3}; do
# shellcheck disable=SC2039
  while ! nc -z db 5432; do
    sleep 0.1
  done
  sleep 1.5
done

echo "PostgreSQL started"

echo "Re-collecting static files"
python manage.py collectstatic --noinput --clear
echo "Static files collected"

echo "Executing database migrations"
python manage.py migrate --noinput
echo "Migrations executed"

exec "$@"