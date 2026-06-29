#!/bin/bash
# Оновлення сайту на сервері після git pull (SSH).
# Запуск: bash deploy/ukraine/update.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

if [ ! -f "$ROOT/.env" ]; then
  echo "Помилка: .env відсутній — не перезаписуйте його при деплої"
  exit 1
fi

if [ ! -d "$ROOT/.venv" ]; then
  echo "Помилка: .venv не знайдено. Запустіть: bash deploy/ukraine/setup.sh"
  exit 1
fi

# shellcheck disable=SC1091
source "$ROOT/.venv/bin/activate"

export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings.hosting}"

echo "==> pip install (якщо змінився requirements.txt)"
pip install -q -r requirements.txt

echo "==> migrate"
python manage.py migrate --noinput

echo "==> collectstatic"
python manage.py collectstatic --noinput

echo "==> check"
python manage.py check --deploy

echo ""
echo "Готово. Далі в adm.tools → Налаштування запуску застосунку → Перезапустити."
