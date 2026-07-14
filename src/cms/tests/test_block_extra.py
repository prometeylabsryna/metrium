from django.test import SimpleTestCase

from src.cms.block_extra import (
    block_has_structured_content,
    parse_faq_items,
    parse_feature_items,
    parse_stat_items,
)
from src.cms.wp_text import sanitize_wp_newlines


class DummyBlock:
    def __init__(self, kind, body="", extra=None):
        self.kind = kind
        self.body = body
        self.extra_data = extra or {}


class WpTextTests(SimpleTestCase):
    def test_sanitize_paragraph_break(self):
        raw = "легалізувати будинок?rnВи звернулися за адресою."
        out = sanitize_wp_newlines(raw)
        self.assertNotIn("rn", out)
        self.assertIn("<br", out)

    def test_sanitize_before_tag(self):
        raw = "<h2>Заголовок</h2>rn<strong>Текст</strong>"
        out = sanitize_wp_newlines(raw)
        self.assertNotIn("rn", out)
        self.assertIn("<strong>Текст</strong>", out)


class BlockExtraTests(SimpleTestCase):
    def test_parse_feature_items(self):
        extra = {
            "items": "4",
            "items_0_title": "Швидкість",
            "items_0_text": "Оперативно.",
            "items_0_ico": "305",
            "items_1_title": "Досвід",
            "items_1_text": "Тисячі об'єктів.",
            "items_1_ico": "182",
        }
        items = parse_feature_items(extra)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["title"], "Швидкість")
        self.assertTrue(items[0]["icon"].endswith("ic1.svg"))

    def test_parse_faq_items(self):
        extra = {
            "items": "2",
            "items_0_title": "Скільки коштує?",
            "items_0_text": "Дивіться калькулятор.",
            "items_1_title": "Як оплатити?",
            "items_1_text": "Безготівково або готівкою.",
        }
        items = parse_faq_items(extra)
        self.assertEqual(len(items), 2)
        self.assertTrue(items[1]["title"].startswith("Як"))

    def test_parse_stat_items(self):
        extra = {
            "b1": '<p><span class="">12</span></p><span>років досвіду</span>',
            "b2": "<p><span>10</span></p><span>філій</span>",
        }
        stats = parse_stat_items(extra)
        self.assertEqual(stats[0], {"value": "12", "label": "років досвіду"})
        self.assertEqual(stats[1]["value"], "10")

    def test_block_has_structured_content(self):
        self.assertTrue(
            block_has_structured_content(
                DummyBlock("faq", extra={"items_0_title": "Q", "items_0_text": "A"})
            )
        )
        self.assertTrue(
            block_has_structured_content(
                DummyBlock(
                    "text",
                    extra={"items_0_title": "Швидкість", "items_0_text": "Так"},
                )
            )
        )
        self.assertFalse(block_has_structured_content(DummyBlock("text", body="коротко")))
