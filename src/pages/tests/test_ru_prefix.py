from django.test import TestCase

from src.pages.ru_prefix import legacy_ru_prefixed_slug, strip_ru_slug_prefix


class RuPrefixHelpersTests(TestCase):
    def test_strip_ru_slug_prefix(self):
        slug, prefixed = strip_ru_slug_prefix("ru-tehnichni-pasporty-bti-brovary")
        self.assertEqual(slug, "tehnichni-pasporty-bti-brovary")
        self.assertTrue(prefixed)

    def test_strip_leaves_normal_slug(self):
        slug, prefixed = strip_ru_slug_prefix("tehnichni-pasporty-bti-brovary")
        self.assertEqual(slug, "tehnichni-pasporty-bti-brovary")
        self.assertFalse(prefixed)

    def test_legacy_prefixed_slug(self):
        self.assertEqual(
            legacy_ru_prefixed_slug("tehnichni-pasporty-bti-brovary"),
            "ru-tehnichni-pasporty-bti-brovary",
        )
