"""Розбір шаблонів на блоки сайту (за HTML-коментарями)."""

from __future__ import annotations

import re
from dataclasses import dataclass

from src.cms.text_keys import (
    T_TAG_RE,
    context_looks_like_faq,
    make_auto_key,
    make_section_label,
    ua_text_is_faq_question,
)

HTML_COMMENT_RE = re.compile(r"<!--\s*(.+?)\s*-->", re.DOTALL)

BLOCK_TITLE_ALIASES: dict[str, str] = {
    "швидке замовлення": "1. Швидке замовлення (форма)",
    "основний опис": "2. Основний опис",
    "вартість": "3. Вартість і калькулятор",
    "коли необхідно виготовляти техпаспорт": "4. Коли потрібен техпаспорт (картки)",
    "виготовлення для інших об'єктів (картки-посилання)": "5. Інші типи паспортів",
    "виготовлення для інших об`єктів (картки-посилання)": "5. Інші типи паспортів",
    "документи для виготовлення": "6. Необхідні документи",
    "калькулятор ціни": "7. Калькулятор",
    "зразок документа": "8. Зразок документа",
    "faq": "9. FAQ (питання й відповіді)",
}


@dataclass(frozen=True)
class TemplateTextItem:
    ua: str
    ru: str
    section_key: str
    block_title: str
    label: str
    is_faq: bool
    sort_order: int


def normalize_block_title(raw: str) -> str:
    cleaned = " ".join(raw.split())
    key = cleaned.lower().rstrip(".")
    if key in BLOCK_TITLE_ALIASES:
        return BLOCK_TITLE_ALIASES[key]
    if key == "faq" or key.startswith("faq "):
        return BLOCK_TITLE_ALIASES["faq"]
    return cleaned


def field_label_for_text(ua: str, *, is_faq: bool, index_in_block: int) -> str:
    text = " ".join(ua.split())
    if is_faq or ua_text_is_faq_question(ua):
        if ua_text_is_faq_question(ua):
            return make_section_label(text, is_faq=True, max_len=100)
        return f"FAQ відповідь: {text[:80]}{'…' if len(text) > 80 else ''}"
    if len(text) <= 70 and not text.endswith((".", "!", "…")):
        return f"Заголовок: {text}"
    preview = text[:90] + ("…" if len(text) > 90 else "")
    if index_in_block <= 1:
        return f"Текст: {preview}"
    return f"Текст {index_in_block}: {preview}"


def extract_template_text_items(content: str) -> list[TemplateTextItem]:
    """Витягує {% t %} з привʼязкою до блоку за найближчим HTML-коментарем вище."""
    comments = [(m.start(), normalize_block_title(m.group(1))) for m in HTML_COMMENT_RE.finditer(content)]

    def block_at(pos: int) -> str:
        current = "0. Hero (банер зверху)"
        for cpos, title in comments:
            if cpos < pos:
                current = title
            else:
                break
        return current

    items: list[TemplateTextItem] = []
    per_block_index: dict[str, int] = {}
    sort_order = 0
    seen_keys: set[str] = set()

    for match in T_TAG_RE.finditer(content):
        ua = match.group(1).replace("\\'", "'")
        ru = match.group(2).replace("\\'", "'")
        explicit_key = match.group(3)
        section_key = explicit_key or make_auto_key(ua, ru)
        if section_key in seen_keys:
            continue
        seen_keys.add(section_key)

        current_block = block_at(match.start())
        is_faq = (
            current_block.startswith("9. FAQ")
            or context_looks_like_faq(content, match.start())
            or ua_text_is_faq_question(ua)
        )
        if is_faq and not current_block.startswith("9. FAQ"):
            current_block = BLOCK_TITLE_ALIASES["faq"]

        per_block_index[current_block] = per_block_index.get(current_block, 0) + 1
        idx = per_block_index[current_block]
        sort_order += 10
        items.append(
            TemplateTextItem(
                ua=ua,
                ru=ru,
                section_key=section_key,
                block_title=current_block,
                label=field_label_for_text(ua, is_faq=is_faq, index_in_block=idx),
                is_faq=is_faq,
                sort_order=sort_order,
            )
        )
    return items
