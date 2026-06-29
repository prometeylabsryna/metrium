from __future__ import annotations

from django.core.cache import cache

from src.cms.models import HomeServiceCard, HomeStatItem, HomeWhyItem, PageSection, SiteImage

SECTION_CACHE_TTL = 300
IMAGE_CACHE_TTL = 300


def _section_cache_key(page_slug: str, section_key: str) -> str:
    return f"section:{page_slug}:{section_key}"


def get_page_section(page_slug: str, section_key: str) -> PageSection | None:
    cache_key = _section_cache_key(page_slug, section_key)
    cached = cache.get(cache_key)
    if cached is not None:
        return cached if cached != "__missing__" else None

    section = PageSection.objects.filter(
        page_slug=page_slug,
        section_key=section_key,
        is_active=True,
    ).first()
    cache.set(cache_key, section or "__missing__", SECTION_CACHE_TTL)
    return section


def get_home_services() -> list[HomeServiceCard]:
    return list(HomeServiceCard.objects.filter(is_active=True).order_by("sort_order", "id"))


def get_home_why_items() -> list[HomeWhyItem]:
    return list(HomeWhyItem.objects.filter(is_active=True).order_by("sort_order", "id"))


def get_home_stats() -> list[HomeStatItem]:
    return list(HomeStatItem.objects.filter(is_active=True).order_by("sort_order", "id"))


def clear_section_cache(page_slug: str = "", section_key: str = "") -> None:
    if page_slug and section_key:
        cache.delete(_section_cache_key(page_slug, section_key))
        return
    for section in PageSection.objects.all().only("page_slug", "section_key"):
        cache.delete(_section_cache_key(section.page_slug, section.section_key))


def _image_cache_key(page_slug: str, image_key: str) -> str:
    return f"site_image:{page_slug}:{image_key}"


def get_site_image(page_slug: str, image_key: str) -> SiteImage | None:
    cache_key = _image_cache_key(page_slug, image_key)
    cached = cache.get(cache_key)
    if cached is not None:
        return cached if cached != "__missing__" else None

    try:
        image = SiteImage.objects.filter(
            page_slug=page_slug,
            image_key=image_key,
            is_active=True,
        ).first()
    except Exception:
        return None
    cache.set(cache_key, image or "__missing__", IMAGE_CACHE_TTL)
    return image


def get_site_images(page_slug: str, key_prefix: str = "") -> list[SiteImage]:
    try:
        qs = SiteImage.objects.filter(page_slug=page_slug, is_active=True)
        if key_prefix:
            qs = qs.filter(image_key__startswith=key_prefix)
        return list(qs.order_by("sort_order", "image_key"))
    except Exception:
        return []


def clear_image_cache(page_slug: str = "", image_key: str = "") -> None:
    if page_slug and image_key:
        cache.delete(_image_cache_key(page_slug, image_key))
        return
    for image in SiteImage.objects.all().only("page_slug", "image_key"):
        cache.delete(_image_cache_key(image.page_slug, image.image_key))
