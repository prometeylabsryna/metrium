#!/bin/bash
# Пакує файли для завантаження на хостинг (без .venv, WP-плагінів, git).
# Запуск: bash deploy/ukraine/pack.sh
# Результат: ../metrium-deploy.tar.gz
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$(dirname "$ROOT")/metrium-deploy.tar.gz"

cd "$ROOT"

if [ ! -f "$ROOT/data/hosting_fixture.json" ]; then
  echo "==> Увага: data/hosting_fixture.json відсутній"
  echo "    Запустіть: bash deploy/ukraine/export_data.sh"
fi

echo "==> Пакування $OUT"

tar -czf "$OUT" \
  --exclude='.venv' \
  --exclude='.git' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.env' \
  --exclude='db.sqlite3' \
  --exclude='staticfiles' \
  --exclude='.DS_Store' \
  --exclude='*.log' \
  --exclude='media' \
  --exclude='archive/wp-admin' \
  --exclude='archive/wp-includes' \
  --exclude='archive/wp-content/plugins' \
  --exclude='archive/wp-content/themes' \
  --exclude='archive/wp-content/cache' \
  --exclude='archive/wp-content/upgrade' \
  --exclude='archive/wp-content/uploads' \
  --exclude='archive-layout' \
  --exclude='archive-layout-v2' \
  --exclude='metrium_prod.sql' \
  --exclude='IMG Metrium' \
  --exclude='Зразки документів Метріум' \
  .

SIZE=$(du -h "$OUT" | cut -f1)
echo "==> Готово: $OUT ($SIZE)"
echo "    Медіа окремо: bash deploy/ukraine/pack_media.sh"
echo "    Розархівуйте у кореневий каталог сайту на хостингу."
