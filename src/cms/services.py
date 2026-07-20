from __future__ import annotations

from django.core.cache import cache

from src.cms.models import HomeServiceCard, HomeStatItem, HomeWhyItem, PageSection, SiteImage

SECTION_CACHE_TTL = 300
IMAGE_CACHE_TTL = 300


def resolve_page_anchor(slug: str):
    """Якір за slug: завжди українська версія з цим slug (якщо є)."""
    from src.i18n.models import Language
    from src.pages.models import StaticPage

    return (
        StaticPage.objects.filter(slug=slug, language=Language.UA).first()
        or StaticPage.objects.filter(slug=slug).order_by("language").first()
    )


def resolve_content_anchor(static_page):
    """Якір контенту для будь-якої мовної версії StaticPage.

    Тексти/фото живуть на одній «якірній» сторінці (зазвичай UA).
    Працює і коли RU має інший slug (напр. golovna / golovna-2) — через
    is_home або translation_group_id.
    """
    from src.i18n.models import Language
    from src.pages.models import StaticPage

    if not static_page:
        return None

    # Головна: контент завжди на UA home, навіть якщо RU slug інший
    if getattr(static_page, "is_home", False) or static_page.slug in ("home", "", "golovna"):
        home = (
            StaticPage.objects.filter(is_home=True, language=Language.UA).first()
            or StaticPage.objects.filter(is_home=True).order_by("language").first()
        )
        if home:
            return home

    # Пара перекладів з різними slug
    group_id = getattr(static_page, "translation_group_id", None)
    if group_id:
        ua = StaticPage.objects.filter(
            translation_group_id=group_id, language=Language.UA
        ).first()
        if ua:
            return ua
        pair = (
            StaticPage.objects.filter(translation_group_id=group_id)
            .order_by("language")
            .first()
        )
        if pair:
            return pair

    return resolve_page_anchor(static_page.slug)


def ensure_static_page_links(static_page) -> None:
    """Прив'язує «безхазяйні» PageSection/SiteImage до їхньої якірної StaticPage.

    Викликається лениво при відкритті сторінки в адмінці — самовідновлювальна
    заміна ручного списку відповідностей slug → page_slug.
    """
    from django.contrib.contenttypes.models import ContentType

    from src.pages.models import StaticPage

    anchor = resolve_content_anchor(static_page)
    if not anchor:
        return

    aliases = {anchor.slug, static_page.slug}
    if anchor.is_home or static_page.is_home:
        aliases.update({"home", "golovna", "golovna-2"})

    content_type = ContentType.objects.get_for_model(StaticPage)
    PageSection.objects.filter(page_slug__in=aliases, content_type__isnull=True).update(
        content_type=content_type, object_id=anchor.pk
    )
    SiteImage.objects.filter(page_slug__in=aliases, content_type__isnull=True).update(
        content_type=content_type, object_id=anchor.pk
    )


def link_all_page_content() -> dict[str, int]:
    """Прив'язує всі PageSection/SiteImage до якірних StaticPage за page_slug."""
    from src.i18n.models import Language
    from src.pages.models import StaticPage

    sections_linked = 0
    images_linked = 0
    pages_touched = 0
    seen_slugs: set[str] = set()

    def _link(page) -> None:
        nonlocal sections_linked, images_linked, pages_touched
        aliases = {page.slug}
        if page.is_home:
            aliases.add("home")
        before_s = PageSection.objects.filter(
            page_slug__in=aliases, content_type__isnull=True
        ).count()
        before_i = SiteImage.objects.filter(
            page_slug__in=aliases, content_type__isnull=True
        ).count()
        ensure_static_page_links(page)
        sections_linked += before_s
        images_linked += before_i
        pages_touched += 1

    for page in StaticPage.objects.filter(language=Language.UA).order_by("slug"):
        seen_slugs.add(page.slug)
        _link(page)

    # Якщо для slug немає UA — якір з першої доступної мови
    for page in StaticPage.objects.exclude(slug__in=seen_slugs).order_by("slug", "language"):
        if page.slug in seen_slugs:
            continue
        seen_slugs.add(page.slug)
        _link(page)

    return {
        "pages": pages_touched,
        "sections": sections_linked,
        "images": images_linked,
    }

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
