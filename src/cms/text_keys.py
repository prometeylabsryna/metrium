from __future__ import annotations

import hashlib
import re

from django.utils.text import slugify

# Підтримка {% t '…' '…' %} і {% t "…" "…" %} (багато сервісних сторінок у подвійних лапках)
_T_STR = r"(['\"])((?:\\.|(?!\1).)*)\1"

T_TAG_RE = re.compile(
    r"\{%\s*t\s+"
    + _T_STR
    + r"\s+"
    + _T_STR
    + r"(?:\s+"
    + _T_STR
    + r")?"
    + r"\s*%\}",
    re.DOTALL,
)

BI_TAG_RE = re.compile(
    r"\{%\s*bi\s+"
    r"['\"]([^'\"]+)['\"]\s+"
    r"['\"]([^'\"]+)['\"]\s+"
    + _T_STR
    + r"\s+"
    + _T_STR
    + r"\s*%\}",
    re.DOTALL | re.IGNORECASE,
)

SECTION_TAG_RE = re.compile(
    r"\{%\s*section\s+"
    r"['\"]([^'\"]+)['\"]\s+"
    r"['\"]([^'\"]+)['\"]\s+"
    + _T_STR
    + r"\s+"
    + _T_STR
    + r"\s*%\}",
    re.DOTALL,
)


def parse_t_tag_match(match: re.Match) -> tuple[str, str, str | None]:
    """Повертає (ua, ru, optional_key) з match T_TAG_RE."""
    ua = match.group(2).replace("\\'", "'").replace('\\"', '"')
    ru = match.group(4).replace("\\'", "'").replace('\\"', '"')
    key = match.group(6)
    if key is not None:
        key = key.replace("\\'", "'").replace('\\"', '"')
    return ua, ru, key


def parse_bi_or_section_texts(match: re.Match) -> tuple[str, str]:
    """UA/RU з bi/section тегів (групи 3–6 після slug і key)."""
    ua = match.group(4).replace("\\'", "'").replace('\\"', '"')
    ru = match.group(6).replace("\\'", "'").replace('\\"', '"')
    return ua, ru

SECTION_BODY_TAG_RE = re.compile(
    r"\{%\s*section_body\s+"
    r"['\"]([^'\"]+)['\"]\s+"
    r"['\"]([^'\"]+)['\"]"
    r"\s*%\}",
)


def make_auto_key(ua_text: str, ru_text: str) -> str:
    digest = hashlib.sha1(f"{ua_text}\0{ru_text}".encode("utf-8")).hexdigest()[:16]
    slug = slugify(ua_text[:48])[:32]
    if slug:
        return f"{slug}-{digest[:8]}"
    return f"t-{digest}"


def make_label(ua_text: str, max_len: int = 120) -> str:
    cleaned = " ".join(ua_text.split())
    if len(cleaned) <= max_len:
        return cleaned
    return f"{cleaned[: max_len - 1]}…"


def make_section_label(ua_text: str, *, is_faq: bool = False, max_len: int = 120) -> str:
    """Людська назва для адмінки; FAQ отримує префікс."""
    base = make_label(ua_text, max_len=max_len - 5 if is_faq else max_len)
    if not is_faq:
        return base
    if base.startswith("FAQ:") or base.startswith("FAQ "):
        return base
    return f"FAQ: {base}"


def context_looks_like_faq(template_content: str, match_start: int, window: int = 800) -> bool:
    """Чи знаходиться {% t %} у блоці FAQ / акордеону."""
    start = max(0, match_start - window)
    chunk = template_content[start:match_start].lower()
    markers = (
        'class="faq',
        "class='faq",
        "<!-- faq",
        'id="accordion',
        "id='accordion",
        "custom-acc",
        'section-label">faq',
        "section-label'>faq",
    )
    return any(marker in chunk for marker in markers)


def ua_text_is_faq_question(ua_text: str) -> bool:
    cleaned = ua_text.strip()
    return cleaned.endswith("?") or cleaned.endswith("？")

def page_slug_from_template_path(path: str) -> str:
    path = path.replace("\\", "/")
    if "partials/header" in path or "partials/mobile_menu" in path:
        return "header"
    if "partials/footer" in path:
        return "footer"
    if "partials/" in path:
        return "global"
    if "pages/home.html" in path:
        return "home"
    if "pages/about.html" in path:
        return "about"
    if "pages/contacts.html" in path:
        return "contacts"
    if "pages/neobhidni" in path:
        return "neobhidni-dokumenty"
    if "reviews/list.html" in path:
        return "reviews"
    if "blog/list.html" in path:
        return "blog"
    if "pages/services/" in path:
        name = path.rsplit("/", 1)[-1].replace(".html", "")
        mapping = {
            "kyiv_oblast": "kyiv-oblast",
            "tehnichni_pasporty": "tehnichni-pasporty-bti",
            "bti_cina": "bti-cina",
            "vvedennya": "vvedennya-v-ekspluatatsiyu",
            "legalizatsiya": "legalizatsiya-neruhomosti",
            "dozvilna": "dozvilna-dokumentatsiya",
            "zemelna": "zemelna-dokumentatsiya",
            "dovidky": "dovidky",
            "poslugy": "poslugy-kyiv",
            "inventaryzatsiya": "tehnichna-inventaryzatsiya",
            "kadastrovyj_nomer": "kadastrovyj-nomer",
            "vytiah_dzk": "vytiah-dzk",
            "vysnovky_bti": "vysnovky-bti",
            "pasport_kvartyra": "tehnichnyj-pasport-na-kvartyru",
            "pasport_budynok": "tehnichnyj-pasport-na-budynok",
            "pasport_elektronnyj": "elektronnyj-tehnichnyj-pasport",
            "pasport_budivlya": "tehnichnyj-pasport-na-budivlyu",
            "pasport_garazh": "tehnichnyj-pasport-na-garazh",
            "pasport_nezhytlove": "tehnichnyj-pasport-na-nezhytlove-prymischennya",
            "pasport_mbd": "tehnichnyj-pasport-na-bagato-kvartyrnyj-budynok",
            "bti_region": "kyiv-oblast",
            "_base_service": "global",
        }
        return mapping.get(name, "global")
    return "global"


def resolve_page_slug(context: dict) -> str:
    explicit = context.get("page_slug")
    if explicit:
        return explicit

    page = context.get("page")
    if page and getattr(page, "slug", None):
        return page.slug

    active_slug = context.get("active_slug")
    if active_slug:
        return active_slug

    request = context.get("request")
    if request:
        path = request.path.strip("/")
        if path.startswith("ru/"):
            path = path[3:]
        if path:
            return path.split("/")[0]

    return "global"
