#!/bin/bash
# Пакує media та legacy WP-завантаження для хостингу.
# Запуск: bash deploy/ukraine/pack_media.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$(dirname "$ROOT")/metrium-media.tar.gz"

cd "$ROOT"

echo "==> Пакування медіа → $OUT"

tar -czf "$OUT" \
  --exclude='.DS_Store' \
  media \
  archive/wp-content/uploads

SIZE=$(du -h "$OUT" | cut -f1)
echo "==> Готово: $OUT ($SIZE)"
echo "    На сервері розархівуйте у корінь сайту (поруч із manage.py)."
