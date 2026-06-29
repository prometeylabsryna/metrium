# Деплой Metrium на Хостинг Україна (adm.tools)

Django 5.2 · Gunicorn · MySQL · UK/RU · адмінка `/admin/`

Тариф **Бізнес 2G** (2048 MB RAM) — підтримує [проксування веб-застосунків](https://www.ukraine.com.ua/wiki/hosting/web-servers/proxying/).

---

## Що вже підготовлено в проєкті

| Компонент | Файл / шлях |
|-----------|-------------|
| Production settings | `config/settings/hosting.py` |
| Gunicorn | `deploy/ukraine/start.sh` |
| Перший запуск (SSH) | `deploy/ukraine/setup.sh` |
| Пакування коду | `deploy/ukraine/pack.sh` |
| Пакування медіа | `deploy/ukraine/pack_media.sh` |
| Експорт / імпорт БД | `deploy/ukraine/export_data.sh`, `import_data.sh` |
| Перевірка після деплою | `deploy/ukraine/verify.sh` |
| Приклад `.env` | `deploy/ukraine/env.example` |

**Мови:** українська (/) та російська (/ru/).  
**Адмінка:** `https://ваш-домен/admin/` (Unfold + TinyMCE).

---

## Крок 1. Підготовка локально

```bash
# 1. Експорт даних з SQLite
bash deploy/ukraine/export_data.sh

# 2. Архів коду (~25 MB без медіа)
bash deploy/ukraine/pack.sh

# 3. Архів медіа (~215 MB)
bash deploy/ukraine/pack_media.sh
```

Результат:
- `../metrium-deploy.tar.gz` — код + `data/hosting_fixture.json`
- `../metrium-media.tar.gz` — `media/` + `archive/wp-content/uploads/`

---

## Крок 2. Налаштування adm.tools

### 2.1 Хостинг-акаунт
- **Python:** 3.10 або новіший (рекомендовано 3.12)
- **SSL:** увімкнути безкоштовний сертифікат для домену

### 2.2 MySQL
1. `MySQL` → створити базу (utf8mb4)
2. Записати: ім'я БД, користувач, пароль, хост (`localhost`)

### 2.3 Сайт
1. `Сайти` → кореневий каталог домену
2. `Налаштування сайту` → **Веб-сервер: Проксування трафіку** → зберегти
3. `Налаштування веб-застосунку`:
   - **Каталог запуску:** корінь сайту (де `manage.py`)
   - **Команда запуску:** `bash deploy/ukraine/start.sh`
   - Скопіювати **IP** (`127.*.*.*`) та **порт** (зазвичай `3000`)

### 2.4 Завантаження файлів
Через **Файл-менеджер** або **SSH / SFTP**:
1. Розархівувати `metrium-deploy.tar.gz` у корінь сайту
2. Розархівувати `metrium-media.tar.gz` у той самий каталог
3. Створити `.env` з `deploy/ukraine/env.example` (заповнити всі поля)

Згенерувати `SECRET_KEY`:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

---

## Крок 3. Перший запуск (SSH)

```bash
cd /шлях/до/кореня/сайту
bash deploy/ukraine/setup.sh
```

Скрипт: venv → pip → migrate → loaddata → collectstatic → check --deploy.

### Адміністратор
Після `loaddata` існує користувач `admin`. **Обов'язково змініть пароль:**
```bash
source .venv/bin/activate
python manage.py changepassword admin
```

Якщо потрібен новий суперкористувач:
```bash
python manage.py createsuperuser
```

---

## Крок 4. Запуск застосунку

У `adm.tools` → `Налаштування веб-застосунку` → **Запустити**.

Перевірка:
```bash
bash deploy/ukraine/verify.sh https://metrium.com.ua
```

Або вручну:
- `https://домен/` — головна (UK)
- `https://домен/ru/` — головна (RU)
- `https://домен/admin/` — адмінка
- `https://домен/healthz/` — `{"status": "ok"}`

---

## Оновлення сайту (реліз)

```bash
# Локально
bash deploy/ukraine/export_data.sh   # якщо змінювалась БД
bash deploy/ukraine/pack.sh

# На сервері
# 1. Завантажити новий архів (без .env і media/)
# 2. SSH:
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate --noinput
python manage.py loaddata data/hosting_fixture.json  # за потреби
python manage.py collectstatic --noinput
# 3. adm.tools → перезапустити веб-застосунок
```

---

## Змінні середовища (.env)

| Змінна | Опис |
|--------|------|
| `SECRET_KEY` | Випадковий ключ ≥50 символів |
| `ALLOWED_HOSTS` | `metrium.com.ua,www.metrium.com.ua` |
| `SITE_URL` | `https://metrium.com.ua` |
| `CSRF_TRUSTED_ORIGINS` | `https://metrium.com.ua,https://www.metrium.com.ua` |
| `MYSQL_*` | Дані з панелі MySQL |
| `APP_BIND_HOST` | IP з блоку «Проксування» (не 0.0.0.0) |
| `APP_BIND_PORT` | Порт з панелі (зазвичай 3000) |
| `GUNICORN_WORKERS` | `2` для Бізнес 2G |
| `EMAIL_*` | SMTP `smtp.ukraine.com.ua:465` (SSL) |

---

## Типові проблеми

| Симптом | Рішення |
|---------|---------|
| 502 / сайт не відкривається | Перевірити логи веб-застосунку в adm.tools; `APP_BIND_HOST`/`PORT` у `.env` |
| Статика адмінки без стилів | `python manage.py collectstatic --noinput` |
| CSRF помилка при логіні | Додати домен у `CSRF_TRUSTED_ORIGINS` з `https://` |
| Зображення не відображаються | Розархівувати `metrium-media.tar.gz`; перевірити `media/` |
| Старі WP-фото | Потрібна папка `archive/wp-content/uploads/` |
| DisallowedHost | Додати домен у `ALLOWED_HOSTS` |

---

## Безпека після деплою

1. Змінити пароль `admin`
2. Увімкнути 2FA в adm.tools
3. Налаштувати захист `/admin/` від брутфорсу (панель хостингу)
4. Не комітити `.env` у git

---

## Структура на сервері

```
корінь-сайту/
├── .env
├── .venv/
├── manage.py
├── config/
├── src/
├── templates/
├── static/
├── staticfiles/      ← після collectstatic
├── media/            ← з metrium-media.tar.gz
├── archive/wp-content/uploads/
├── data/hosting_fixture.json
└── deploy/ukraine/
```
