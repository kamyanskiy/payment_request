#!/bin/sh

# PostgreSQL is ready (via healthcheck)
echo "Running migrations..."
uv run python manage.py migrate --no-input
uv run python manage.py compilemessages -l en -l ru

# it will use env variables DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_PASSWORD
uv run python manage.py createsuperuser --noinput || true

uv run python manage.py collectstatic --noinput

exec "$@"
