from __future__ import annotations

from django.core.cache import cache

from src.core.models import SitePhone, SiteSettings

SETTINGS_CACHE_KEY = "site:settings"
PHONES_CACHE_KEY = "site:phones"


def get_site_settings() -> SiteSettings | None:
    cached = cache.get(SETTINGS_CACHE_KEY)
    if cached is not None:
        return cached
    settings_obj = SiteSettings.objects.first()
    if settings_obj:
        cache.set(SETTINGS_CACHE_KEY, settings_obj, 300)
    return settings_obj


def get_site_phones() -> list[dict[str, str]]:
    cached = cache.get(PHONES_CACHE_KEY)
    if cached is not None:
        return cached

    settings_obj = get_site_settings()
    if settings_obj:
        phones = [
            {"number": phone.tel_href, "display": phone.display}
            for phone in settings_obj.phones.filter(is_active=True).order_by("sort_order", "id")
        ]
    else:
        phones = [
            {"number": "tel:0673986200", "display": "067-398-62-00"},
            {"number": "tel:0500672060", "display": "050-067-20-60"},
        ]

    cache.set(PHONES_CACHE_KEY, phones, 300)
    return phones


def get_messengers() -> dict[str, str]:
    settings_obj = get_site_settings()
    if not settings_obj:
        return {
            "telegram": "https://telegram.me/metriumbti",
            "viber": "viber://chat?number=%2B380673986200",
            "whatsapp": "https://wa.me/380673986200",
            "instagram": "https://www.instagram.com/pruvatnebti",
            "facebook": "https://www.facebook.com/profile.php?id=61584165429803",
        }
    return {
        "telegram": settings_obj.telegram,
        "viber": settings_obj.viber,
        "whatsapp": settings_obj.whatsapp,
        "instagram": settings_obj.instagram,
        "facebook": settings_obj.facebook,
    }


def clear_site_cache() -> None:
    cache.delete(SETTINGS_CACHE_KEY)
    cache.delete(PHONES_CACHE_KEY)
