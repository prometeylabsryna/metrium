from django.test import SimpleTestCase

from src.cms.image_size_hints import HINT_DOC_EXAMPLE, HINT_HERO_DESKTOP, hint_for_site_image


class ImageSizeHintsTests(SimpleTestCase):
    def test_hero_and_doc_hints(self):
        self.assertEqual(hint_for_site_image("hero"), HINT_HERO_DESKTOP)
        self.assertIn("400×520", hint_for_site_image("hero", mobile=True))
        self.assertEqual(hint_for_site_image("doc.example"), HINT_DOC_EXAMPLE)
