from pathlib import Path

from decouple import config
from django.urls import reverse_lazy

from config.pulse_chat import (
    PULSE_CONNECT_SRC,
    PULSE_FONT_SRC,
    PULSE_FRAME_SRC,
    PULSE_LIVE_CHAT_ID_DEFAULT,
    PULSE_MEDIA_SRC,
    PULSE_SCRIPT_SRC,
    PULSE_STYLE_SRC,
    PULSE_WORKER_SRC,
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config("SECRET_KEY")

DEBUG = False

ALLOWED_HOSTS: list[str] = config(
    "ALLOWED_HOSTS",
    default="localhost,127.0.0.1",
    cast=lambda v: [s.strip() for s in v.split(",") if s.strip()],
)

INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "tinymce",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "django_htmx",
    "csp",
    "src.core",
    "src.i18n",
    "src.pages",
    "src.cms",
    "src.blog",
    "src.seo",
    "src.redirects",
    "src.leads",
    "src.reviews",
    "src.migration",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "src.redirects.middleware.RedirectMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "src.i18n.middleware.PolylangCompatMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "csp.middleware.CSPMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "src.core.context_processors.site_context",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_DB", default="metrium"),
        "USER": config("POSTGRES_USER", default="metrium"),
        "PASSWORD": config("POSTGRES_PASSWORD", default="metrium"),
        "HOST": config("POSTGRES_HOST", default="localhost"),
        "PORT": config("POSTGRES_PORT", default="5432"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "uk"
LANGUAGES = [
    ("uk", "Українська"),
    ("ru", "Русский"),
]
LOCALE_PATHS = [BASE_DIR / "locale"]

TIME_ZONE = "Europe/Kyiv"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

WP_UPLOADS_ROOT = BASE_DIR / "archive" / "wp-content" / "uploads"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SITE_URL = config("SITE_URL", default="https://metrium.com.ua")
SITE_NAME = "Metrium"

PULSE_LIVE_CHAT_ID = config("PULSE_LIVE_CHAT_ID", default=PULSE_LIVE_CHAT_ID_DEFAULT)
PULSE_LIVE_CHAT_ENABLED = config("PULSE_LIVE_CHAT_ENABLED", default=True, cast=bool)

WORDPRESS_SQL_PATH = config(
    "WORDPRESS_SQL_PATH",
    default=str(BASE_DIR / "metrium_prod.sql"),
)
HTACCESS_PATH = config(
    "HTACCESS_PATH",
    default=str(BASE_DIR / "archive" / ".htaccess"),
)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
    },
    "root": {"handlers": ["console"], "level": "WARNING"},
    "loggers": {
        "src": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "django": {"handlers": ["console"], "level": "WARNING", "propagate": False},
    },
}

CONTENT_SECURITY_POLICY = {
    # Admin excluded from CSP (Alpine.js / Unfold needs unsafe-eval there too).
    # Public site: Pulse.is live chat bundle.js uses new Function() — needs unsafe-eval.
    "EXCLUDE_URL_PREFIXES": ("/admin/",),
    "DIRECTIVES": {
        "default-src": ("'self'",),
        "script-src": (
            "'self'",
            "'unsafe-eval'",
            "https://www.googletagmanager.com",
            "https://www.google-analytics.com",
            "https://www.google.com",
            "https://www.googleadservices.com",
            "https://googleads.g.doubleclick.net",
            "https://pagead2.googlesyndication.com",
            "https://www.gstatic.com",
            *PULSE_SCRIPT_SRC,
            "https://cdn.jsdelivr.net",
        ),
        "style-src": (
            "'self'",
            "'unsafe-inline'",
            "https://fonts.googleapis.com",
            "https://cdnjs.cloudflare.com",
            *PULSE_STYLE_SRC,
            "https://cdn.jsdelivr.net",
        ),
        "font-src": (
            "'self'",
            "https://fonts.gstatic.com",
            "https://cdn.jsdelivr.net",
            *PULSE_FONT_SRC,
        ),
        "img-src": ("'self'", "data:", "https:", "blob:"),
        "connect-src": (
            "'self'",
            "https://www.google-analytics.com",
            "https://analytics.google.com",
            "https://region1.google-analytics.com",
            "https://stats.g.doubleclick.net",
            "https://www.googletagmanager.com",
            "https://www.google.com",
            "https://google.com",
            "https://www.google.com.ua",
            "https://google.com.ua",
            "https://googleads.g.doubleclick.net",
            "https://ad.doubleclick.net",
            "https://www.googleadservices.com",
            "https://pagead2.googlesyndication.com",
            "https://cdnjs.cloudflare.com",
            *PULSE_CONNECT_SRC,
        ),
        "media-src": (
            "'self'",
            *PULSE_MEDIA_SRC,
        ),
        "worker-src": (
            "'self'",
            *PULSE_WORKER_SRC,
        ),
        "frame-src": (
            "https://www.googletagmanager.com",
            "https://www.openstreetmap.org",
            "https://www.google.com",
            "https://maps.google.com",
            "https://googleads.g.doubleclick.net",
            "https://ad.doubleclick.net",
            "https://td.doubleclick.net",
            *PULSE_FRAME_SRC,
        ),
        "frame-ancestors": ("'none'",),
    },
}

TELEGRAM_BOT_TOKEN = config("TELEGRAM_BOT_TOKEN", default="")
TELEGRAM_CHAT_ID = config("TELEGRAM_CHAT_ID", default="")
TELEGRAM_AGENT_BOT_TOKEN = config("TELEGRAM_AGENT_BOT_TOKEN", default="")
TELEGRAM_AGENT_CHAT_ID = config("TELEGRAM_AGENT_CHAT_ID", default="")
LEADS_EMAIL = config("LEADS_EMAIL", default="pruvatnebti@gmail.com")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="noreply@metrium.com.ua")

TINYMCE_DEFAULT_CONFIG = {
    "height": 360,
    "menubar": False,
    "plugins": "link lists table code",
    "toolbar": "undo redo | bold italic underline | bullist numlist | link | removeformat",
    "language": "uk",
}

UNFOLD = {
    "SITE_TITLE": "Metrium",
    "SITE_HEADER": "Metrium БТІ",
    "SITE_SUBHEADER": "Панель керування сайтом",
    "SITE_SYMBOL": "business",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "COLORS": {
        "primary": {
            "50": "240 249 255",
            "100": "224 242 254",
            "200": "186 230 253",
            "300": "125 211 252",
            "400": "56 189 248",
            "500": "14 165 233",
            "600": "2 132 199",
            "700": "3 105 161",
            "800": "7 89 133",
            "900": "12 74 110",
            "950": "8 47 73",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Сторінки",
                "separator": True,
                "collapsible": False,
                "items": [
                    {
                        "title": "Усі сторінки сайту",
                        "icon": "description",
                        "link": reverse_lazy("admin:pages_staticpage_changelist"),
                    },
                    {
                        "title": "Головна",
                        "icon": "home",
                        "link": "/admin/pages/staticpage/?page_kind=home",
                    },
                    {
                        "title": "Контакти",
                        "icon": "call",
                        "link": "/admin/pages/staticpage/?page_kind=contacts",
                    },
                    {
                        "title": "Блог (сторінка)",
                        "icon": "article",
                        "link": "/admin/pages/staticpage/?page_kind=blog",
                    },
                    {
                        "title": "Регіональні",
                        "icon": "map",
                        "link": "/admin/pages/staticpage/?page_kind=region",
                    },
                ],
            },
            {
                "title": "Технічні паспорти",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Усі техпаспорти",
                        "icon": "folder",
                        "link": "/admin/pages/staticpage/?page_kind=passport",
                    },
                    {
                        "title": "На квартиру",
                        "icon": "apartment",
                        "link": "/admin/pages/staticpage/?slug__exact=tehnichnyj-pasport-na-kvartyru",
                    },
                    {
                        "title": "На будинок",
                        "icon": "house",
                        "link": "/admin/pages/staticpage/?slug__exact=tehnichnyj-pasport-na-budynok",
                    },
                    {
                        "title": "Електронний",
                        "icon": "devices",
                        "link": "/admin/pages/staticpage/?slug__exact=elektronnyj-tehnichnyj-pasport",
                    },
                    {
                        "title": "На будівлю",
                        "icon": "domain",
                        "link": "/admin/pages/staticpage/?slug__exact=tehnichnyj-pasport-na-budivlyu",
                    },
                    {
                        "title": "На гараж",
                        "icon": "garage",
                        "link": "/admin/pages/staticpage/?slug__exact=tehnichnyj-pasport-na-garazh",
                    },
                    {
                        "title": "Нежитлове",
                        "icon": "store",
                        "link": "/admin/pages/staticpage/?slug__exact=tehnichnyj-pasport-na-nezhytlove-prymischennya",
                    },
                    {
                        "title": "Багатоквартирний",
                        "icon": "location_city",
                        "link": "/admin/pages/staticpage/?slug__exact=tehnichnyj-pasport-na-bagato-kvartyrnyj-budynok",
                    },
                ],
            },
            {
                "title": "Інші послуги БТІ",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Усі інші послуги",
                        "icon": "folder_open",
                        "link": "/admin/pages/staticpage/?page_kind=services",
                    },
                    {
                        "title": "Довідки БТІ",
                        "icon": "description",
                        "link": "/admin/pages/staticpage/?slug__exact=dovidky",
                    },
                    {
                        "title": "Введення в експлуатацію",
                        "icon": "key",
                        "link": "/admin/pages/staticpage/?slug__exact=vvedennya-v-ekspluatatsiyu",
                    },
                    {
                        "title": "Легалізація",
                        "icon": "gavel",
                        "link": "/admin/pages/staticpage/?slug__exact=legalizatsiya-neruhomosti",
                    },
                    {
                        "title": "Інвентаризація",
                        "icon": "inventory_2",
                        "link": "/admin/pages/staticpage/?slug__exact=tehnichna-inventaryzatsiya",
                    },
                    {
                        "title": "Дозвільна документація",
                        "icon": "assignment",
                        "link": "/admin/pages/staticpage/?slug__exact=dozvilna-dokumentatsiya",
                    },
                    {
                        "title": "Земельна документація",
                        "icon": "landscape",
                        "link": "/admin/pages/staticpage/?slug__exact=zemelna-dokumentatsiya",
                    },
                    {
                        "title": "Висновки БТІ",
                        "icon": "fact_check",
                        "link": "/admin/pages/staticpage/?slug__exact=vysnovky-bti",
                    },
                    {
                        "title": "Кадастровий номер",
                        "icon": "tag",
                        "link": "/admin/pages/staticpage/?slug__exact=kadastrovyj-nomer",
                    },
                    {
                        "title": "Витяг ДЗК",
                        "icon": "article",
                        "link": "/admin/pages/staticpage/?slug__exact=vytiah-dzk",
                    },
                ],
            },
            {
                "title": "Головна сторінка",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Послуги на головній",
                        "icon": "grid_view",
                        "link": reverse_lazy("admin:cms_homeservicecard_changelist"),
                    },
                    {
                        "title": "Переваги на головній",
                        "icon": "verified",
                        "link": reverse_lazy("admin:cms_homewhyitem_changelist"),
                    },
                    {
                        "title": "Статистика на головній",
                        "icon": "analytics",
                        "link": reverse_lazy("admin:cms_homestatitem_changelist"),
                    },
                ],
            },
            {
                "title": "Спільні елементи",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Лого, Hero, контакти, футер",
                        "icon": "settings",
                        "link": reverse_lazy("admin:core_sitesettings_changelist"),
                    },
                    {
                        "title": "Меню (шапка)",
                        "icon": "menu",
                        "link": "/admin/cms/pagesection/?page_slug__exact=header",
                    },
                    {
                        "title": "Футер",
                        "icon": "bottom_navigation",
                        "link": "/admin/cms/pagesection/?page_slug__exact=footer",
                    },
                    {
                        "title": "Загальні тексти (форми, popup)",
                        "icon": "translate",
                        "link": "/admin/cms/pagesection/?page_slug__exact=global",
                    },
                    {
                        "title": "Офіси на карті",
                        "icon": "location_on",
                        "link": reverse_lazy("admin:core_office_changelist"),
                    },
                ],
            },
            {
                "title": "Контент",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Блог",
                        "icon": "newspaper",
                        "link": reverse_lazy("admin:blog_blogpost_changelist"),
                    },
                    {
                        "title": "Відгуки",
                        "icon": "star",
                        "link": reverse_lazy("admin:reviews_review_changelist"),
                    },
                    {
                        "title": "SEO метадані",
                        "icon": "search",
                        "link": reverse_lazy("admin:seo_seometadata_changelist"),
                    },
                ],
            },
            {
                "title": "Заявки",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Всі заявки",
                        "icon": "inbox",
                        "link": reverse_lazy("admin:leads_leadsubmission_changelist"),
                    },
                ],
            },
            {
                "title": "Службове",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Усі тексти сторінок (пошук)",
                        "icon": "view_quilt",
                        "link": reverse_lazy("admin:cms_pagesection_changelist"),
                    },
                    {
                        "title": "Усі зображення сайту (пошук)",
                        "icon": "image",
                        "link": reverse_lazy("admin:cms_siteimage_changelist"),
                    },
                    {
                        "title": "Блоки конструктора",
                        "icon": "widgets",
                        "link": reverse_lazy("admin:cms_pageblock_changelist"),
                    },
                    {
                        "title": "Редіректи",
                        "icon": "sync_alt",
                        "link": reverse_lazy("admin:redirects_redirectrule_changelist"),
                    },
                    {
                        "title": "Користувачі",
                        "icon": "person",
                        "link": reverse_lazy("admin:auth_user_changelist"),
                    },
                ],
            },
        ],
    },
}
