#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

# Run database migrations
python manage.py migrate
python manage.py create_superusers
python manage.py create_cities
python manage.py create_countys_and_countrires
python manage.py create_uk
# Start Gunicorn
exec "$@"