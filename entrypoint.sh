#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

# Run database migrations
python manage.py migrate
python manage.py create_superusers

# Start Gunicorn
exec "$@"