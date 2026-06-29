#!/bin/bash
# Первинне налаштування проєкту на Хостинг Україна (SSH).
# Запуск: bash deploy/ukraine/setup.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

VENV="$ROOT/.venv"

for candidate in python3.12 python3.11 python3.10 python3; do
  if command -v "$candidate" >/dev/null 2>&1; then
    PYTHON="$candidate"
    break
  fi
done

if [ -z "${PYTHON:-}" ]; then
  echo "Помилка: Python 3.10+ не знайдено"
  exit 1
fi

echo "==> Metrium — setup на adm.tools"
echo "    Каталог: $ROOT"
echo "    Python:  $($PYTHON --version)"

if [ ! -f "$ROOT/.env" ]; then
  echo "Помилка: створіть .env з deploy/ukraine/env.example"
  exit 1
fi

if [ ! -d "$VENV" ]; then
  echo "==> venv ($PYTHON)"
  "$PYTHON" -m venv "$VENV"
fi

# shellcheck disable=SC1091
source "$VENV/bin/activate"

export DJANGO_SETTINGS_MODULE=config.settings.hosting

echo "==> pip install"
pip install --upgrade pip
pip install -r requirements.txt

echo "==> migrate"
python manage.py migrate --noinput

if [ -f "$ROOT/data/hosting_fixture.json" ]; then
  echo "==> loaddata"
  python manage.py loaddata "$ROOT/data/hosting_fixture.json"
else
  echo "==> Увага: data/hosting_fixture.json відсутній — БД порожня"
fi

echo "==> collectstatic"
python manage.py collectstatic --noinput

echo "==> check --deploy"
python manage.py check --deploy

echo ""
echo "Готово. Далі в adm.tools:"
echo "  1. Налаштування сайту → Веб-сервер → Проксування трафіку"
echo "  2. Налаштування веб-застосунку → команда: bash deploy/ukraine/start.sh"
echo "  3. IP і порт з панелі — у .env (APP_BIND_HOST, APP_BIND_PORT)"
echo "  4. Змініть пароль: python manage.py changepassword admin"
