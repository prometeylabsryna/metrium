from django import template
from django.utils.safestring import mark_safe

from src.cms.services import get_page_section
from src.cms.text_keys import make_auto_key, resolve_page_slug

register = template.Library()


def _localized_section_value(section_obj, language: str) -> str:
    value = section_obj.localized_text(language) or section_obj.localized_body(language)
    return value.strip() if value else ""


def _lookup_text(context, ua_text: str, ru_text: str, section_key: str | None = None) -> str:
    language = context.get("current_language", "ua")
    page_slug = resolve_page_slug(context)
    key = section_key or make_auto_key(ua_text, ru_text)

    for slug in (page_slug, "global"):
        section_obj = get_page_section(slug, key)
        if section_obj:
            value = _localized_section_value(section_obj, language)
            if value:
                if "<" in value:
                    return mark_safe(value)
                return value.replace("\n", "<br>") if "\n" in value else value

    return ru_text if language == "ru" else ua_text


@register.simple_tag(takes_context=True)
def t(context, ua_text, ru_text=None, section_key=None):
    """UA/RU text with optional PageSection override from admin."""
    if ru_text is None:
        ru_text = ua_text
    return _lookup_text(context, ua_text, ru_text, section_key)


@register.simple_tag(takes_context=True)
def bi(context, page_slug, section_key, ua_text, ru_text=None):
    """Bilingual text from PageSection with template fallbacks."""
    if ru_text is None:
        ru_text = ua_text
    language = context.get("current_language", "ua")
    section_obj = get_page_section(page_slug, section_key)
    if section_obj:
        value = _localized_section_value(section_obj, language)
        if value:
            if "<" in value:
                return mark_safe(value)
            return value
    return ru_text if language == "ru" else ua_text


@register.simple_tag(takes_context=True)
def lang_url(context, path="/"):
    """Build internal URL with /ru/ prefix when needed."""
    prefix = context.get("lang_prefix", "")
    if not path.startswith("/"):
        path = f"/{path}"
    if path == "/":
        url = f"{prefix}/" if prefix else "/"
        if prefix == "/ru":
            url = f"{url}?hl=ru"
        return url
    return f"{prefix}{path}"
