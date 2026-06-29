#!/bin/bash
# Імпорт даних на хостинг після migrate.
# Запуск: bash deploy/ukraine/import_data.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

FIXTURE="$ROOT/data/hosting_fixture.json"

if [ ! -f "$FIXTURE" ]; then
  echo "Помилка: не знайдено $FIXTURE"
  echo "Спочатку локально: bash deploy/ukraine/export_data.sh"
  exit 1
fi

# shellcheck disable=SC1091
source "$ROOT/.venv/bin/activate"

export DJANGO_SETTINGS_MODULE=config.settings.hosting

echo "==> Імпорт даних з $FIXTURE"
python manage.py loaddata "$FIXTURE"
echo "==> Готово. Змініть пароль адміна: python manage.py changepassword admin"
