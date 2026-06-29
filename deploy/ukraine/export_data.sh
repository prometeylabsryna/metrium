#!/bin/bash
# Експорт даних з локальної БД для імпорту на хостинг (MySQL).
# Запуск: bash deploy/ukraine/export_data.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

OUT="$ROOT/data/hosting_fixture.json"
mkdir -p "$ROOT/data"

# shellcheck disable=SC1091
source "$ROOT/.venv/bin/activate"

export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings.develop}"

echo "==> Експорт даних → $OUT"

python manage.py dumpdata \
  --natural-foreign --natural-primary \
  --indent 2 \
  -e contenttypes \
  -e auth.permission \
  -e sessions.session \
  -o "$OUT"

SIZE=$(du -h "$OUT" | cut -f1)
echo "==> Готово: $OUT ($SIZE)"
echo "    Завантажте на сервер разом із кодом або окремо."
