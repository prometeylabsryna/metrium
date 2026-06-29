from django.conf import settings

from src.core.services import get_messengers, get_site_phones, get_site_settings


def _alternate_language_url(path: str, target_language: str) -> str:
    """Build alternate-language URL with ?hl= to bypass cached legacy 301 on /ru/."""
    stripped = path.rstrip("/")
    if stripped.startswith("/ru"):
        stripped = stripped[3:] or "/"
    if not stripped.startswith("/"):
        stripped = f"/{stripped}"
    if target_language == "ru":
        base = "/ru/" if stripped == "/" else f"/ru{stripped}/"
    else:
        base = "/" if stripped == "/" else f"{stripped}/"
    return f"{base}?hl={target_language}"


def site_context(request):
    path = request.path
    current_language = "ru" if path == "/ru/" or path.startswith("/ru/") else "ua"
    alternate_language = "ua" if current_language == "ru" else "ru"
    lang_prefix = "/ru" if current_language == "ru" else ""

    stripped = path.strip("/")
    if stripped.startswith("ru/"):
        stripped = stripped[3:]
    slug = stripped.split("/")[0] if stripped else ""
    page_slug = slug or "home"

    return {
        "SITE_URL": settings.SITE_URL,
        "SITE_NAME": settings.SITE_NAME,
        "PULSE_LIVE_CHAT_ID": settings.PULSE_LIVE_CHAT_ID,
        "PULSE_LIVE_CHAT_ENABLED": settings.PULSE_LIVE_CHAT_ENABLED,
        "current_language": current_language,
        "alternate_language": alternate_language,
        "lang_prefix": lang_prefix,
        "alternate_language_url": _alternate_language_url(path, alternate_language),
        "active_slug": slug,
        "page_slug": page_slug,
        "PHONES": get_site_phones(),
        "MESSENGERS": get_messengers(),
        "SITE_SETTINGS": get_site_settings(),
    }
