"""Offline parser for WordPress MySQL dumps (metrium_prod.sql)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator


UA_LANG_TAX_ID = 2
RU_LANG_TAX_ID = 5
FRONT_PAGE_IDS = {9, 12590}


@dataclass
class WpPost:
    id: int
    post_name: str
    post_title: str
    post_type: str
    post_status: str
    post_parent: int
    post_date: str
    post_modified: str
    post_content: str = ""
    post_excerpt: str = ""


@dataclass
class WpSeoRow:
    post_id: int
    title: str = ""
    description: str = ""
    canonical_url: str = ""
    og_title: str = ""
    og_description: str = ""
    og_image_url: str = ""
    robots_noindex: bool = False
    robots_nofollow: bool = False
    schema: str = ""
    priority: str | None = None
    frequency: str | None = None


@dataclass
class WpRedirect:
    url_from: str
    url_to: str
    status: int


@dataclass
class WpData:
    posts: dict[int, WpPost] = field(default_factory=dict)
    postmeta: dict[int, dict[str, str]] = field(default_factory=dict)
    post_language: dict[int, str] = field(default_factory=dict)
    translation_groups: dict[int, dict[str, int]] = field(default_factory=dict)
    seo: dict[int, WpSeoRow] = field(default_factory=dict)
    redirects: list[WpRedirect] = field(default_factory=list)
    attachment_paths: dict[int, str] = field(default_factory=dict)


def _split_sql_values(row: str) -> list[str]:
    """Split a single SQL VALUES tuple respecting quoted strings."""
    values: list[str] = []
    current: list[str] = []
    in_string = False
    escape = False
    quote_char = ""
    for ch in row:
        if escape:
            current.append(ch)
            escape = False
            continue
        if ch == "\\" and in_string:
            escape = True
            continue
        if in_string:
            if ch == quote_char:
                in_string = False
            current.append(ch)
            continue
        if ch in ("'", '"'):
            in_string = True
            quote_char = ch
            current.append(ch)
            continue
        if ch == ",":
            values.append("".join(current).strip())
            current = []
            continue
        current.append(ch)
    if current:
        values.append("".join(current).strip())
    return values


def _unquote(val: str) -> str:
    val = val.strip()
    if val == "NULL":
        return ""
    if (val.startswith("'") and val.endswith("'")) or (
        val.startswith('"') and val.endswith('"')
    ):
        inner = val[1:-1]
        return inner.replace("\\'", "'").replace('\\"', '"').replace("\\\\", "\\")
    return val


def _parse_insert_rows(chunk: str) -> Iterator[list[str]]:
    depth = 0
    current: list[str] = []
    in_string = False
    escape = False
    quote_char = ""
    for ch in chunk:
        if escape:
            current.append(ch)
            escape = False
            continue
        if ch == "\\" and in_string:
            escape = True
            current.append(ch)
            continue
        if in_string:
            if ch == quote_char:
                in_string = False
            current.append(ch)
            continue
        if ch in ("'", '"'):
            in_string = True
            quote_char = ch
            current.append(ch)
            continue
        if ch == "(":
            if depth == 0:
                current = []
            else:
                current.append(ch)
            depth += 1
            continue
        if ch == ")":
            depth -= 1
            if depth == 0:
                yield _split_sql_values("".join(current))
            else:
                current.append(ch)
            continue
        if depth > 0:
            current.append(ch)


def _values_chunk(insert_sql: str) -> str:
    """Return only the VALUES tuples portion of an INSERT statement."""
    upper = insert_sql.upper()
    idx = upper.rfind(" VALUES")
    if idx == -1:
        return ""
    return insert_sql[idx + len(" VALUES") :]


def _iter_table_inserts(sql_path: Path, table: str) -> Iterator[list[str]]:
    marker = f"INSERT INTO `{table}`"
    collecting = False
    buffer = ""
    with sql_path.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if not collecting:
                if marker in line:
                    collecting = True
                    buffer = line
                    if line.rstrip().endswith(";"):
                        chunk = _values_chunk(buffer)
                        if chunk:
                            for row in _parse_insert_rows(chunk):
                                yield row
                        collecting = False
                        buffer = ""
                continue
            buffer += line
            if line.rstrip().endswith(";"):
                chunk = _values_chunk(buffer)
                if chunk:
                    for row in _parse_insert_rows(chunk):
                        yield row
                collecting = False
                buffer = ""


def parse_php_serialized_dict(raw: str) -> dict[str, int]:
    """Parse Polylang post_translations PHP serialized arrays."""
    if not raw:
        return {}
    pairs = re.findall(r's:\d+:"([^"]+)";i:(\d+)', raw)
    return {lang: int(pid) for lang, pid in pairs}


def build_url_path(
    slug: str, language: str, post_type: str, *, wp_id: int | None = None
) -> str:
    prefix = "/ru" if language == "ru" else ""
    if wp_id in FRONT_PAGE_IDS or slug in ("home", "index"):
        return f"{prefix}/" if prefix else "/"
    if post_type == "blogs":
        return f"{prefix}/blogs/{slug}/"
    if post_type == "page":
        return f"{prefix}/{slug}/" if slug else f"{prefix}/"
    return f"{prefix}/{post_type}/{slug}/"


def parse_htaccess_gone(htaccess_path: Path) -> list[str]:
    paths: list[str] = []
    pattern = re.compile(r"^Redirect\s+410\s+(/[^\s]+)\s*$", re.MULTILINE)
    text = htaccess_path.read_text(encoding="utf-8", errors="replace")
    for match in pattern.finditer(text):
        path = match.group(1).rstrip("/") or "/"
        paths.append(path)
    return paths


def load_wordpress_sql(sql_path: Path) -> WpData:
    data = WpData()

    for row in _iter_table_inserts(sql_path, "kt_posts"):
        if len(row) < 21:
            continue
        try:
            post_id = int(_unquote(row[0]))
        except ValueError:
            continue
        post = WpPost(
            id=post_id,
            post_name=_unquote(row[11]),
            post_title=_unquote(row[5]),
            post_type=_unquote(row[20]),
            post_status=_unquote(row[7]),
            post_parent=int(_unquote(row[17]) or 0),
            post_date=_unquote(row[2]),
            post_modified=_unquote(row[15]),
            post_content=_unquote(row[4]),
            post_excerpt=_unquote(row[6]) if len(row) > 6 else "",
        )
        data.posts[post_id] = post
        if post.post_type == "attachment":
            guid = _unquote(row[18])
            if "/wp-content/uploads/" in guid:
                rel = guid.split("/wp-content/uploads/", 1)[1]
                data.attachment_paths[post_id] = rel

    for row in _iter_table_inserts(sql_path, "kt_postmeta"):
        if len(row) < 4:
            continue
        try:
            post_id = int(_unquote(row[1]))
        except ValueError:
            continue
        key = _unquote(row[2])
        value = _unquote(row[3])
        data.postmeta.setdefault(post_id, {})[key] = value

    for row in _iter_table_inserts(sql_path, "kt_term_relationships"):
        if len(row) < 2:
            continue
        try:
            object_id = int(_unquote(row[0]))
            tax_id = int(_unquote(row[1]))
        except ValueError:
            continue
        if tax_id == UA_LANG_TAX_ID:
            data.post_language[object_id] = "ua"
        elif tax_id == RU_LANG_TAX_ID:
            data.post_language[object_id] = "ru"

    for row in _iter_table_inserts(sql_path, "kt_term_taxonomy"):
        if len(row) < 4:
            continue
        if _unquote(row[2]) != "post_translations":
            continue
        desc = _unquote(row[3])
        group = parse_php_serialized_dict(desc)
        if group:
            try:
                term_id = int(_unquote(row[1]))
            except ValueError:
                continue
            data.translation_groups[term_id] = {
                str(k): int(v) for k, v in group.items()
            }

    post_to_group: dict[int, int] = {}
    for term_id, group in data.translation_groups.items():
        for post_id in group.values():
            post_to_group[post_id] = term_id

    for row in _iter_table_inserts(sql_path, "kt_aioseo_posts"):
        if len(row) < 3:
            continue
        try:
            post_id = int(_unquote(row[1]))
        except ValueError:
            continue
        seo = WpSeoRow(
            post_id=post_id,
            title=_unquote(row[2]),
            description=_unquote(row[3]) if len(row) > 3 else "",
            canonical_url=_unquote(row[8]) if len(row) > 8 else "",
            og_title=_unquote(row[9]) if len(row) > 9 else "",
            og_description=_unquote(row[10]) if len(row) > 10 else "",
            og_image_url=_unquote(row[13]) if len(row) > 13 else "",
            robots_noindex=_unquote(row[36]) == "1" if len(row) > 36 else False,
            robots_nofollow=_unquote(row[39]) == "1" if len(row) > 39 else False,
            schema=_unquote(row[31]) if len(row) > 31 else "",
            priority=_unquote(row[48]) if len(row) > 48 else None,
            frequency=_unquote(row[49]) if len(row) > 49 else None,
        )
        data.seo[post_id] = seo

    for row in _iter_table_inserts(sql_path, "kt_redirects"):
        if len(row) < 4:
            continue
        try:
            status = int(_unquote(row[3]) or 301)
        except ValueError:
            continue
        data.redirects.append(
            WpRedirect(
                url_from=_unquote(row[1]),
                url_to=_unquote(row[2]),
                status=status,
            )
        )

    return data


def export_manifest_entries(data: WpData) -> list[dict[str, Any]]:
    """Build SEO manifest rows for published content."""
    entries: list[dict[str, Any]] = []
    post_to_group: dict[int, dict[str, int]] = {}
    for group in data.translation_groups.values():
        for lang, pid in group.items():
            post_to_group[pid] = group

    for post_id, post in data.posts.items():
        if post.post_status != "publish":
            continue
        if post.post_type not in ("page", "blogs", "service", "revs", "post"):
            continue
        language = data.post_language.get(post_id, "ua")
        path = build_url_path(
            post.post_name, language, post.post_type, wp_id=post_id
        )
        seo = data.seo.get(post_id)
        group = post_to_group.get(post_id, {})
        hreflang: dict[str, str] = {}
        for lang, pid in group.items():
            if pid in data.posts:
                p = data.posts[pid]
                hreflang[lang] = build_url_path(
                    p.post_name, lang, p.post_type, wp_id=pid
                )

        entries.append(
            {
                "wp_id": post_id,
                "path": path,
                "slug": post.post_name,
                "language": language,
                "post_type": post.post_type,
                "title": post.post_title,
                "seo_title": seo.title if seo else "",
                "seo_description": seo.description if seo else "",
                "canonical": seo.canonical_url if seo else "",
                "robots_noindex": seo.robots_noindex if seo else False,
                "hreflang": hreflang,
                "template": data.postmeta.get(post_id, {}).get("_wp_page_template", ""),
            }
        )
    entries.sort(key=lambda e: e["path"])
    return entries
