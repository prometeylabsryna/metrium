from pathlib import Path

from django.conf import settings
from django.test import TestCase

from src.cms.template_blocks import extract_template_text_items, normalize_block_title


class TemplateBlocksTests(TestCase):
    def test_normalize_known_comment(self):
        self.assertEqual(
            normalize_block_title("Основний опис"),
            "2. Основний опис",
        )

    def test_pasport_kvartyra_has_intro_and_faq_blocks(self):
        path = Path(settings.BASE_DIR) / "templates/pages/services/pasport_kvartyra.html"
        items = extract_template_text_items(path.read_text(encoding="utf-8"))
        titles = {item.block_title for item in items}
        self.assertIn("2. Основний опис", titles)
        self.assertIn("3. Вартість і калькулятор", titles)
        self.assertIn("4. Коли потрібен техпаспорт (картки)", titles)
        self.assertIn("9. FAQ (питання й відповіді)", titles)
        intro = [i for i in items if i.block_title == "2. Основний опис"]
        self.assertEqual(len(intro), 1)
        self.assertIn("офіційний інформаційний документ", intro[0].ua)
