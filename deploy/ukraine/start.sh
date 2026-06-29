#!/bin/bash
# Запуск Gunicorn для панелі adm.tools (Налаштування веб-застосунку).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

if [ -f "$ROOT/.env" ]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT/.env"
  set +a
fi

if [ ! -d "$ROOT/.venv" ]; then
  echo "Помилка: .venv не знайдено. Запустіть: bash deploy/ukraine/setup.sh"
  exit 1
fi

# shellcheck disable=SC1091
source "$ROOT/.venv/bin/activate"

export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings.hosting}"

BIND_HOST="${APP_BIND_HOST:?Вкажіть APP_BIND_HOST у .env (IP з панелі adm.tools)}"
BIND_PORT="${APP_BIND_PORT:?Вкажіть APP_BIND_PORT у .env (порт з панелі adm.tools)}"

WORKERS="${GUNICORN_WORKERS:-2}"
THREADS="${GUNICORN_THREADS:-2}"
TIMEOUT="${GUNICORN_TIMEOUT:-120}"

exec gunicorn config.wsgi:application \
  --bind "${BIND_HOST}:${BIND_PORT}" \
  --workers "$WORKERS" \
  --threads "$THREADS" \
  --timeout "$TIMEOUT" \
  --access-logfile - \
  --error-logfile - \
  --capture-output
