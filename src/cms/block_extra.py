"""Extract structured ACF extra_data for CMS block rendering."""

from __future__ import annotations

import re
from html import unescape
from typing import Any

from django.utils.html import strip_tags

from src.cms.wp_text import sanitize_wp_newlines

_ITEM_KEY_RE = re.compile(r"^items_(\d+)_(.+)$")
_STAT_KEY_RE = re.compile(r"^b(\d+)$")
_FALLBACK_ICONS = (
    "images/kata/ic1.svg",
    "images/kata/ic2.svg",
    "images/kata/ic3.svg",
    "images/kata/ic4.svg",
)


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    text = sanitize_wp_newlines(str(value))
    text = unescape(text)
    return " ".join(text.split()).strip()


def _plain_len(value: str) -> int:
    return len(" ".join(strip_tags(value or "").split()))


def parse_feature_items(extra: dict | None) -> list[dict[str, str]]:
    """ACF items_N_title / items_N_text (/ items_N_ico) → feature cards."""
    extra = extra or {}
    buckets: dict[int, dict[str, str]] = {}
    for key, raw in extra.items():
        match = _ITEM_KEY_RE.match(str(key))
        if not match:
            continue
        index = int(match.group(1))
        field = match.group(2)
        if field not in ("title", "text", "ico", "isRed"):
            continue
        buckets.setdefault(index, {})[field] = raw if raw is not None else ""

    items: list[dict[str, str]] = []
    for index in sorted(buckets):
        row = buckets[index]
        title = _clean_text(row.get("title", ""))
        text = _clean_text(row.get("text", ""))
        if not title and not text:
            continue
        icon_raw = str(row.get("ico") or "").strip()
        # WP attachment IDs are digits — use rotating static icons instead.
        if icon_raw.isdigit() or not icon_raw:
            icon = _FALLBACK_ICONS[index % len(_FALLBACK_ICONS)]
        else:
            icon = icon_raw
        items.append({"title": title, "text": text, "icon": icon})
    return items


def parse_faq_items(extra: dict | None) -> list[dict[str, str]]:
    """ACF FAQ items_N_title / items_N_text."""
    items = []
    for item in parse_feature_items(extra):
        if not item["title"]:
            continue
        items.append({"title": item["title"], "text": item["text"]})
    return items


def parse_stat_items(extra: dict | None) -> list[dict[str, str]]:
    """ACF b1..bN HTML snippets → value + label."""
    extra = extra or {}
    stats: list[tuple[int, dict[str, str]]] = []
    for key, raw in extra.items():
        match = _STAT_KEY_RE.match(str(key))
        if not match or raw is None:
            continue
        html = str(raw)
        spans = re.findall(r"<span[^>]*>(.*?)</span>", html, flags=re.I | re.S)
        spans = [_clean_text(strip_tags(s)) for s in spans if _clean_text(strip_tags(s))]
        if len(spans) >= 2:
            value, label = spans[0], spans[1]
        else:
            plain = _clean_text(strip_tags(html))
            parts = plain.split(None, 1)
            if not parts:
                continue
            value = parts[0]
            label = parts[1] if len(parts) > 1 else ""
        if value:
            stats.append((int(match.group(1)), {"value": value, "label": label}))
    stats.sort(key=lambda pair: pair[0])
    return [item for _, item in stats]


def block_has_structured_content(block) -> bool:
    extra = getattr(block, "extra_data", None) or {}
    kind = getattr(block, "kind", "") or ""
    if kind == "faq":
        return bool(parse_faq_items(extra))
    if kind in ("text", "seo_text", "html"):
        if parse_feature_items(extra) or parse_stat_items(extra):
            return True
    if kind == "gallery":
        return True
    return False


def block_body_plain_len(block) -> int:
    return _plain_len(getattr(block, "body", "") or "")
