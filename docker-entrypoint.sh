#!/bin/bash

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput

echo "Apply database migrations"
python manage.py migrate

# Start server
echo "Starting server"
python manage.py runserver --insecure 0.0.0.0:8000