#!/bin/sh
set -e

echo "Waiting for database..."
python - <<'PY'
import os, time
import psycopg2
host = os.environ.get("POSTGRES_HOST", "db")
for i in range(30):
    try:
        psycopg2.connect(
            dbname=os.environ.get("POSTGRES_DB", "metrium"),
            user=os.environ.get("POSTGRES_USER", "metrium"),
            password=os.environ.get("POSTGRES_PASSWORD", "metrium"),
            host=host,
            port=os.environ.get("POSTGRES_PORT", "5432"),
        )
        break
    except Exception:
        time.sleep(1)
else:
    raise SystemExit("Database not ready")
PY

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
