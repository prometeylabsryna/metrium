import json

from django import template
from django.utils.safestring import mark_safe

from src.seo.services import (
    build_canonical_url,
    build_robots_directive,
    get_seo_for_object,
    hreflang_code,
    organization_schema,
)

register = template.Library()


@register.inclusion_tag("seo/meta.html", takes_context=True)
def seo_meta(context, obj=None):
    request = context["request"]
    obj = obj or context.get("page") or context.get("post")
    seo = get_seo_for_object(obj) if obj else None
    page_title = ""
    if seo and seo.seo_title:
        page_title = seo.seo_title
    elif obj and hasattr(obj, "title"):
        page_title = obj.title
    else:
        page_title = "Metrium"

    alternates = []
    if obj and hasattr(obj, "get_translation"):
        for lang in ("ua", "ru"):
            trans = obj.get_translation(lang)
            if trans:
                alternates.append(
                    {
                        "hreflang": hreflang_code(lang),
                        "href": request.build_absolute_uri(trans.get_absolute_url()),
                    }
                )
    elif context.get("alternate_language_url"):
        current = context.get("current_language", "ua")
        alternate = context.get("alternate_language", "ru" if current == "ua" else "ua")
        alternates = [
            {
                "hreflang": hreflang_code(current),
                "href": request.build_absolute_uri(request.path),
            },
            {
                "hreflang": hreflang_code(alternate),
                "href": request.build_absolute_uri(context["alternate_language_url"]),
            },
        ]

    schema_data = organization_schema()
    if seo and seo.schema_json:
        try:
            schema_data = json.loads(seo.schema_json)
        except json.JSONDecodeError:
            pass

    return {
        "page_title": page_title,
        "seo_description": seo.seo_description if seo else "",
        "canonical_url": build_canonical_url(obj, seo, request) if obj else request.build_absolute_uri("/"),
        "robots": build_robots_directive(seo),
        "og_title": (seo.og_title or page_title) if seo else page_title,
        "og_description": seo.og_description if seo else "",
        "og_image": seo.og_image_url if seo else "",
        "alternates": alternates,
        "schema_json": mark_safe(json.dumps(schema_data, ensure_ascii=False)),
    }
