#!/bin/bash
set -e

# Ensure directories exist
mkdir -p /app/session_cookies /app/logs

# Run database migrations
echo "[ENTRYPOINT] Applying database migrations..."
python manage.py makemigrations panel --noinput || true
python manage.py migrate --noinput

# Execute command
echo "[ENTRYPOINT] Launching container command: $@"
exec "$@"
