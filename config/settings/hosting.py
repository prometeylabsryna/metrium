"""Production settings for Хостинг Україна (adm.tools) — бізнес-хостинг + проксування."""

import pymysql

from decouple import config

from .production import *  # noqa: F403

pymysql.install_as_MySQLdb()

SERVE_USER_UPLOADS = True

_db_engine = config("DB_ENGINE", default="mysql").lower()

if _db_engine == "mysql":
    DATABASES = {  # noqa: F405
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": config("MYSQL_DATABASE"),
            "USER": config("MYSQL_USER"),
            "PASSWORD": config("MYSQL_PASSWORD"),
            "HOST": config("MYSQL_HOST", default="localhost"),
            "PORT": config("MYSQL_PORT", default="3306"),
            "CONN_MAX_AGE": 60,
            "OPTIONS": {
                "charset": "utf8mb4",
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST", default="smtp.ukraine.com.ua")
EMAIL_PORT = config("EMAIL_PORT", default=465, cast=int)
EMAIL_USE_SSL = config("EMAIL_USE_SSL", default=True, cast=bool)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=False, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "metrium-hosting",
    }
}

LOGGING["handlers"]["console"]["level"] = "INFO"  # noqa: F405
LOGGING["loggers"]["django"]["level"] = "ERROR"  # noqa: F405
