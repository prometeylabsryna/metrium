#!/bin/bash
# Перевірка роботи сайту після деплою.
# Запуск: bash deploy/ukraine/verify.sh [BASE_URL]
set -euo pipefail

BASE="${1:-${SITE_URL:-https://metrium.com.ua}}"
BASE="${BASE%/}"

check() {
  local path="$1"
  local expect="$2"
  local code
  code=$(curl -sS -o /dev/null -w "%{http_code}" "${BASE}${path}")
  if [ "$code" = "$expect" ]; then
    echo "OK  $code  ${path}"
  else
    echo "FAIL expected=$expect got=$code  ${path}"
    return 1
  fi
}

echo "==> Перевірка $BASE"
check "/healthz/" "200"
check "/" "200"
check "/ru/" "200"
check "/admin/login/" "200"
check "/robots.txt" "200"
check "/sitemap.xml" "200"
echo "==> Усі перевірки пройдено"
