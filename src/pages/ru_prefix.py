"""Helpers for legacy WordPress RU slugs prefixed with ``ru-``."""

RU_SLUG_PREFIX = "ru-"


def strip_ru_slug_prefix(slug: str) -> tuple[str, bool]:
    """Return ``(normalized_slug, was_prefixed)``."""
    if slug.startswith(RU_SLUG_PREFIX) and len(slug) > len(RU_SLUG_PREFIX):
        return slug[len(RU_SLUG_PREFIX) :], True
    return slug, False


def legacy_ru_prefixed_slug(slug: str) -> str:
    """Build legacy WP slug ``ru-{slug}`` for fallback lookups."""
    return f"{RU_SLUG_PREFIX}{slug}"
