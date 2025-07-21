#!/bin/bash

echo "Starting up the container..."

echo "Applying migrations..."
python manage.py makemigrations users
python manage.py makemigrations app
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Uvicorn server..."
exec uvicorn Ecommerce.asgi:application --host 0.0.0.0 --port 8000 --reload
