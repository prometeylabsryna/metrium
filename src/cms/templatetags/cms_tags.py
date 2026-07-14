from django import template
from pathlib import Path
from django.templatetags.static import static
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe

from src.cms.block_extra import block_has_structured_content
from src.cms.services import get_home_services, get_home_stats, get_home_why_items, get_page_section, get_site_image, get_site_images

register = template.Library()

BLOCK_TEMPLATES = {
    "banner": "cms/blocks/banner.html",
    "text": "cms/blocks/text.html",
    "calculator": "cms/blocks/calculator.html",
    "services": "cms/blocks/services.html",
    "price_list": "cms/blocks/price_list.html",
    "lead_form": "cms/blocks/lead_form.html",
    "faq": "cms/blocks/faq.html",
    "reviews": "cms/blocks/reviews.html",
    "seo_text": "cms/blocks/seo_text.html",
    "map": "cms/blocks/map.html",
    "video": "cms/blocks/video.html",
    "gallery": "cms/blocks/gallery.html",
    "steps": "cms/blocks/steps.html",
    "brands": "cms/blocks/brands.html",
    "contacts": "cms/blocks/contacts.html",
    "main_links": "cms/blocks/main_links.html",
    "garanty": "cms/blocks/garanty.html",
    "html": "cms/blocks/html.html",
}

# HTML-блоки без реального тексту лишають порожні секції з padding 72px
_CONTENT_KINDS = frozenset({"text", "seo_text", "html", "faq"})
_FALLBACK_BEFORE = frozenset({"calculator", "lead_form", "price_list", "faq", "reviews"})
_MIN_BODY_CHARS = 40


def _plain_text_len(value: str) -> int:
    return len(" ".join(strip_tags(value or "").split()))


def _block_is_renderable(block) -> bool:
    kind = getattr(block, "kind", "") or ""
    heading = (getattr(block, "heading", "") or "").strip()
    body_len = _plain_text_len(getattr(block, "body", "") or "")

    if kind not in _CONTENT_KINDS:
        return True
    if body_len >= _MIN_BODY_CHARS:
        return True
    if block_has_structured_content(block):
        return True
    # Заголовок без тіла → «дірки» на city-сторінках після WP-імпорту
    if kind == "text":
        return False
    if kind == "seo_text":
        return False
    if kind == "faq":
        return bool(heading and body_len > 0)
    if kind == "html":
        return body_len > 0
    return bool(heading)


def _blocks_need_content_fallback(blocks) -> bool:
    for block in blocks:
        kind = getattr(block, "kind", "") or ""
        if kind not in _CONTENT_KINDS:
            continue
        if _plain_text_len(getattr(block, "body", "") or "") >= _MIN_BODY_CHARS:
            return False
        if block_has_structured_content(block):
            return False
    return True


@register.inclusion_tag("cms/render_inner.html", takes_context=True)
def render_blocks(context, blocks):
    block_list = list(blocks or [])
    rendered = []
    needs_fallback = _blocks_need_content_fallback(block_list)
    fallback_inserted = False

    for block in block_list:
        if not _block_is_renderable(block):
            continue
        if needs_fallback and not fallback_inserted and block.kind in _FALLBACK_BEFORE:
            rendered.append(
                {
                    "is_fallback": True,
                    "template": "cms/partials/constructor_content_fallback.html",
                    "block": None,
                }
            )
            fallback_inserted = True
        tpl = BLOCK_TEMPLATES.get(block.kind, "cms/blocks/html.html")
        rendered.append({"is_fallback": False, "block": block, "template": tpl})

    if needs_fallback and not fallback_inserted:
        rendered.append(
            {
                "is_fallback": True,
                "template": "cms/partials/constructor_content_fallback.html",
                "block": None,
            }
        )

    return {
        "blocks": rendered,
        "request": context.get("request"),
        "page": context.get("page"),
        "page_slug": context.get("page_slug") or getattr(context.get("page"), "slug", "") or "",
        "current_language": context.get("current_language"),
    }


@register.simple_tag(takes_context=True)
def fetch_section(context, page_slug, section_key):
    language = context.get("current_language", "ua")
    section_obj = get_page_section(page_slug, section_key)
    if not section_obj:
        return ""
    return section_obj.localized_text(language) or section_obj.localized_body(language)


@register.simple_tag(takes_context=True)
def section(context, page_slug, section_key, default_ua="", default_ru=""):
    language = context.get("current_language", "ua")
    section_obj = get_page_section(page_slug, section_key)
    if section_obj:
        value = section_obj.localized_text(language)
        if value:
            return mark_safe(value.replace("\n", "<br>")) if "<" not in value else mark_safe(value)
    return mark_safe((default_ru if language == "ru" else default_ua).replace("\n", "<br>"))


@register.simple_tag(takes_context=True)
def section_body(context, page_slug, section_key, default_ua="", default_ru=""):
    language = context.get("current_language", "ua")
    section_obj = get_page_section(page_slug, section_key)
    if section_obj:
        value = section_obj.localized_body(language) or section_obj.localized_text(language)
        if value:
            return mark_safe(value)
    return mark_safe(default_ru if language == "ru" else default_ua)


@register.simple_tag(takes_context=True)
def section_image(context, page_slug, section_key):
    section_obj = get_page_section(page_slug, section_key)
    if section_obj and section_obj.image:
        language = context.get("current_language", "ua")
        return {
            "url": section_obj.image.url,
            "alt": section_obj.localized_image_alt(language),
        }
    return None


@register.simple_tag
def home_services():
    return get_home_services()


@register.simple_tag
def home_why_items():
    return get_home_why_items()


@register.simple_tag
def home_stats():
    return get_home_stats()


def _resolve_image_url(image_obj, field_name: str, fallback_field: str, fallback_static: str) -> str:
    file_field = getattr(image_obj, field_name, None) if image_obj else None
    if file_field:
        return file_field.url
    if image_obj and getattr(image_obj, fallback_field, ""):
        return static(getattr(image_obj, fallback_field))
    if fallback_static:
        return static(fallback_static)
    return ""


@register.simple_tag(takes_context=True)
def site_image_url(context, page_slug, image_key, fallback_static=""):
    obj = get_site_image(page_slug, image_key)
    return _resolve_image_url(obj, "image", "fallback_static", fallback_static)


@register.simple_tag(takes_context=True)
def site_image_mobile_url(context, page_slug, image_key, fallback_static=""):
    obj = get_site_image(page_slug, image_key)
    url = _resolve_image_url(obj, "image_mobile", "fallback_static_mobile", fallback_static)
    if url:
        return url
    return site_image_url(context, page_slug, image_key, fallback_static)


@register.simple_tag(takes_context=True)
def site_image_alt(context, page_slug, image_key, fallback_ua="", fallback_ru=""):
    language = context.get("current_language", "ua")
    obj = get_site_image(page_slug, image_key)
    if obj:
        alt = obj.localized_alt(language)
        if alt:
            return alt
    return fallback_ru if language == "ru" else fallback_ua


@register.simple_tag(takes_context=True)
def kata_img(context, page_slug, filename):
    """Зображення з images/kata/ — редагується в SiteImage (ключ static.<ім'я>)."""
    static_path = f"images/kata/{filename}"
    image_key = f"static.{Path(filename).stem}"
    return site_image_url(context, page_slug, image_key, static_path)


@register.inclusion_tag("cms/partials/hero_banner.html", takes_context=True)
def hero_banner(context):
    page_slug = context.get("page_slug", "")
    language = context.get("current_language", "ua")
    obj = get_site_image(page_slug, "hero") if page_slug else None
    desktop = _resolve_image_url(
        obj,
        "image",
        "fallback_static",
        "images/kata/tehnichnyj-pasport.webp",
    )
    mobile = _resolve_image_url(
        obj,
        "image_mobile",
        "fallback_static_mobile",
        "images/kata/tehnichnyj-pasport-3.webp",
    )
    alt = ""
    if obj:
        alt = obj.localized_alt(language)
    return {
        "desktop_url": desktop,
        "mobile_url": mobile or desktop,
        "alt": alt,
    }


@register.inclusion_tag("cms/partials/gallery_images.html", takes_context=True)
def gallery_images(context, page_slug, key_prefix):
    language = context.get("current_language", "ua")
    items = _gallery_items(page_slug, key_prefix, language)
    if not items and key_prefix == "gallery.marquee.":
        for index in range(1, 6):
            path = f"images/kata/foto{index}.webp"
            items.append(
                {
                    "url": static(path),
                    "alt": "Фото роботи БТІ Метріум" if language != "ru" else "Фото работы БТИ Метриум",
                }
            )
    return {"images": items, "language": language}


def _gallery_items(page_slug: str, key_prefix: str, language: str) -> list[dict]:
    items = []
    for image in get_site_images(page_slug, key_prefix):
        url = _resolve_image_url(image, "image", "fallback_static", "")
        if not url:
            continue
        items.append(
            {
                "url": url,
                "alt": image.localized_alt(language) or image.label,
            }
        )
    return items


@register.inclusion_tag("cms/partials/gallery_portfolio.html", takes_context=True)
def gallery_portfolio(context, page_slug, key_prefix):
    language = context.get("current_language", "ua")
    items = _gallery_items(page_slug, key_prefix, language)
    if not items and key_prefix == "gallery.portfolio.":
        defaults = [
            ("images/kata/Tehpasport-na-kvartyru-1.png", "Зразок технічного паспорта на квартиру", "Образец технического паспорта на квартиру"),
            ("images/kata/Tehpasport-na-kvartyru-2.png", "Зразок технічного паспорта на квартиру", "Образец технического паспорта на квартиру"),
            ("images/kata/Tehpasport-na-budynok-1.png", "Зразок технічного паспорта на будинок", "Образец технического паспорта на дом"),
            ("images/kata/Tehpasport-na-budynok-2.png", "Зразок технічного паспорта на будинок", "Образец технического паспорта на дом"),
            ("images/kata/Tehpasport-na-budynok-3.png", "Зразок технічного паспорта на будинок", "Образец технического паспорта на дом"),
        ]
        for path, alt_ua, alt_ru in defaults:
            items.append(
                {
                    "url": static(path),
                    "alt": alt_ru if language == "ru" else alt_ua,
                }
            )
    return {"images": items, "language": language}
