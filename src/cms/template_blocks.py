"""Розбір шаблонів на блоки сайту (за HTML-коментарями)."""

from __future__ import annotations

import re
from dataclasses import dataclass

from src.cms.text_keys import (
    T_TAG_RE,
    context_looks_like_faq,
    make_auto_key,
    parse_t_tag_match,
    ua_text_is_faq_question,
)

HTML_COMMENT_RE = re.compile(r"<!--\s*(.+?)\s*-->", re.DOTALL)

BLOCK_TITLE_ALIASES: dict[str, str] = {
    "швидке замовлення": "1. Швидке замовлення (форма)",
    "форма прийому телефону": "1. Швидке замовлення (форма)",
    "основний опис": "2. Основний опис",
    "що таке дозвільна документація": "2. Основний опис",
    "для чого потрібна довідка з бті": "4. Для чого потрібна довідка",
    "вартість": "3. Вартість і калькулятор",
    "коли необхідно виготовляти техпаспорт": "4. Коли потрібен техпаспорт (картки)",
    "коли варто замовити техпаспорт": "4. Коли потрібен техпаспорт (картки)",
    "в яких випадках потрібен техпаспорт": "4. Коли потрібен техпаспорт (картки)",
    "коли варто виготовляти технічний паспорт": "4. Коли потрібен техпаспорт (картки)",
    "у яких випадках потрібен": "4. Коли потрібен техпаспорт (картки)",
    "виготовлення для інших об'єктів (картки-посилання)": "5. Інші типи паспортів",
    "виготовлення для інших об`єктів (картки-посилання)": "5. Інші типи паспортів",
    "виготовлення для вашого об'єкта (картки-посилання)": "5. Типи об'єктів",
    "документи для виготовлення": "6. Необхідні документи",
    "документи для виготовлення (tabs)": "6. Необхідні документи",
    "необхідні документи": "6. Необхідні документи",
    "документи": "6. Необхідні документи",
    "етапи та документи": "6. Етапи та документи",
    "калькулятор ціни": "7. Калькулятор",
    "калькулятор": "7. Калькулятор",
    "зразок документа": "8. Зразок документа",
    "термін дії": "8. Термін дії",
    "строки": "8. Строки",
    "faq": "9. FAQ (питання й відповіді)",
    "об'єкти будівництва": "4. Об'єкти будівництва",
    "порядок введення в експлуатацію": "5. Порядок введення",
    "технічна інвентаризація: які документи ми оформляємо": "4. Які документи оформляємо",
    "інструкція, порядок проведення, постанова 488": "5. Порядок проведення",
    "переваги оформлення у метріум": "4. Переваги",
    "фото техпаспорта (бігова стрічка, аналогічна до \"фото наших робіт\" на головній)": "8. Фото техпаспорта",
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
    """Короткий підпис ролі — повний текст лише в textarea, без обрізання «…»."""
    text = " ".join(ua.split())
    if is_faq or ua_text_is_faq_question(ua):
        if ua_text_is_faq_question(ua):
            return f"FAQ · питання {index_in_block}"
        return f"FAQ · відповідь {index_in_block}"
    if len(text) <= 70 and not text.endswith((".", "!", "…")):
        return "Заголовок" if index_in_block <= 1 else f"Заголовок {index_in_block}"
    return "Текст" if index_in_block <= 1 else f"Текст {index_in_block}"


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
        ua, ru, explicit_key = parse_t_tag_match(match)
        section_key = explicit_key or make_auto_key(ua, ru)
        if section_key in seen_keys:
            continue
        seen_keys.add(section_key)

        # Блок лише з HTML-коментаря / акордеону FAQ — НЕ з «?» у тексті
        # (інакше «Маєте питання?» розриває «Основний опис» і плодить дублікати FAQ)
        current_block = block_at(match.start())
        in_faq_markup = context_looks_like_faq(content, match.start())
        if in_faq_markup and not current_block.startswith("9. FAQ"):
            current_block = BLOCK_TITLE_ALIASES["faq"]
        is_faq = current_block.startswith("9. FAQ") or in_faq_markup

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
