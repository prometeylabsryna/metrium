from django.test import SimpleTestCase

from src.cms.template_blocks import extract_template_text_items
from src.cms.text_keys import T_TAG_RE, parse_t_tag_match


class TTagQuotesTests(SimpleTestCase):
    def test_single_and_double_quotes(self):
        html = """
        <!-- Основний опис -->
        {% t 'Текст UA' 'Текст RU' %}
        {% t "Довідка БТІ" "Справка БТИ" %}
        """
        items = extract_template_text_items(html)
        texts = {i.ua for i in items}
        self.assertIn("Текст UA", texts)
        self.assertIn("Довідка БТІ", texts)
        for item in items:
            if item.ua == "Довідка БТІ":
                self.assertEqual(item.block_title, "2. Основний опис")

    def test_parse_t_tag_match_groups(self):
        m = T_TAG_RE.search("{% t \"А\" \"Б\" %}")
        self.assertIsNotNone(m)
        ua, ru, key = parse_t_tag_match(m)
        self.assertEqual(ua, "А")
        self.assertEqual(ru, "Б")
        self.assertIsNone(key)
