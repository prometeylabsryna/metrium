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
