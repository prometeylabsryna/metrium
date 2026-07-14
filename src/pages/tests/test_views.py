from django.test import TestCase

from src.pages.models import StaticPage


class PageDetailViewTests(TestCase):
    def setUp(self):
        StaticPage.objects.create(
            slug="golovna",
            title="Головна",
            language="ua",
            is_published=True,
            is_home=True,
        )

    def test_home_returns_200(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_ru_city_page_after_normalize(self):
        StaticPage.objects.create(
            slug="tehnichni-pasporty-bti-brovary",
            title="Техпаспорт Бровары",
            language="ru",
            is_published=True,
            template_key="template-constructor.php",
        )
        response = self.client.get("/ru/tehnichni-pasporty-bti-brovary/")
        self.assertEqual(response.status_code, 200)

    def test_ru_city_page_legacy_prefixed_slug_fallback(self):
        StaticPage.objects.create(
            slug="ru-tehnichni-pasporty-bti-brovary",
            title="Техпаспорт Бровары",
            language="ua",
            is_published=True,
            template_key="template-constructor.php",
        )
        response = self.client.get("/ru/tehnichni-pasporty-bti-brovary/")
        self.assertEqual(response.status_code, 200)
