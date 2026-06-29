"""Parse ACF flexible content blocks from WordPress postmeta."""

from __future__ import annotations

import re
from typing import Any

from src.cms.models import BlockKind


LAYOUT_TO_KIND: dict[str, str] = {
    "calculator": BlockKind.CALCULATOR,
    "calc": BlockKind.CALCULATOR,
    "services": BlockKind.SERVICES,
    "services2": BlockKind.SERVICES,
    "price": BlockKind.PRICE_LIST,
    "pnevmo": BlockKind.PRICE_LIST,
    "order": BlockKind.LEAD_FORM,
    "sto_form": BlockKind.LEAD_FORM,
    "sto_form2": BlockKind.LEAD_FORM,
    "sto_form3": BlockKind.LEAD_FORM,
    "faq": BlockKind.FAQ,
    "revs": BlockKind.REVIEWS,
    "seo": BlockKind.SEO_TEXT,
    "maps": BlockKind.MAP,
    "video": BlockKind.VIDEO,
    "video-youtube": BlockKind.VIDEO,
    "foto-portfolio": BlockKind.GALLERY,
    "brands": BlockKind.BRANDS,
    "steps": BlockKind.STEPS,
    "block1": BlockKind.BANNER,
    "block2": BlockKind.BANNER,
    "block3": BlockKind.TEXT,
    "block4": BlockKind.TEXT,
    "block5": BlockKind.TEXT,
    "block6": BlockKind.TEXT,
    "block18": BlockKind.TEXT,
    "about": BlockKind.TEXT,
    "about2": BlockKind.TEXT,
    "about-gray": BlockKind.TEXT,
    "about-center": BlockKind.TEXT,
    "about_descr": BlockKind.TEXT,
    "garanty_black": BlockKind.TEXT,
    "garanty_light": BlockKind.TEXT,
    "cats": BlockKind.TEXT,
    "main-links": BlockKind.TEXT,
    "contacts": BlockKind.TEXT,
}


def _parse_blocks_layouts(raw: str) -> list[str]:
    """Extract ACF flexible layout names from PHP serialized `blocks` meta."""
    if not raw:
        return []
    if raw.isdigit():
        return [""] * int(raw)
    return re.findall(r's:\d+:"([^"]+)"', raw)


def _block_indices(postmeta: dict[str, str]) -> list[int]:
    indices: set[int] = set()
    for key in postmeta:
        match = re.match(r"blocks_(\d+)_", key)
        if match and not key.startswith("_blocks_"):
            indices.add(int(match.group(1)))
    return sorted(indices)


def parse_acf_blocks(postmeta: dict[str, str]) -> list[dict[str, Any]]:
    """Return ordered block dicts from ACF postmeta keys."""
    raw_blocks = postmeta.get("blocks", "") or ""
    layouts = _parse_blocks_layouts(raw_blocks)
    indices = _block_indices(postmeta)
    if layouts:
        count = len(layouts)
    elif indices:
        count = max(indices) + 1
        layouts = [""] * count
    else:
        return []

    blocks: list[dict[str, Any]] = []
    for i in range(count):
        prefix = f"blocks_{i}_"
        layout = layouts[i] if i < len(layouts) else ""
        if not layout:
            layout = postmeta.get(f"{prefix}acf_fc_layout", "") or "html"
        kind = LAYOUT_TO_KIND.get(layout, BlockKind.HTML)
        fields: dict[str, Any] = {"layout": layout, "kind": kind, "sort_order": i * 10}
        for key, val in postmeta.items():
            if not key.startswith(prefix) or key.startswith(f"_{prefix}"):
                continue
            field_name = key[len(prefix) :]
            if field_name in ("acf_fc_layout",):
                continue
            if field_name in ("title", "zagolovok", "heading", "zagolovok_golovnij"):
                fields["heading"] = val
            elif field_name in ("descr", "text", "tekst", "body", "tekst_na_pershomu_baneri"):
                fields["body"] = (fields.get("body", "") + "\n" + val).strip()
            elif field_name in ("fon", "zobrazhennya_na_baneri", "img", "image"):
                fields.setdefault("extra_data", {})["image_id"] = val
            else:
                fields.setdefault("extra_data", {})[field_name] = val
        blocks.append(fields)
    return blocks
