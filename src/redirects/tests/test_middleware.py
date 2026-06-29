from django.test import TestCase

from src.redirects.middleware import RedirectMiddleware
from src.redirects.models import RedirectRule


class RedirectMiddlewareTests(TestCase):
    def setUp(self):
        RedirectMiddleware.clear_cache()
        RedirectRule.objects.create(
            source_path="/gone-page",
            status_code=410,
            target_url="",
        )

    def test_gone_returns_410(self):
        response = self.client.get("/gone-page/")
        self.assertEqual(response.status_code, 410)

    def test_ru_homepage_not_redirected_by_legacy_rule(self):
        RedirectRule.objects.create(
            source_path="/ru",
            target_url="/golovna/",
            status_code=301,
        )
        RedirectMiddleware.clear_cache()
        response = self.client.get("/ru/")
        self.assertEqual(response.status_code, 200)

    def test_uk_prefix_redirects_to_home(self):
        RedirectMiddleware.clear_cache()
        response = self.client.get("/uk/")
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response["Location"], "/")

    def test_typo_pasport_slug_redirects(self):
        RedirectMiddleware.clear_cache()
        response = self.client.get("/teknichnyj-pasport-na-budynok/")
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response["Location"], "/tehnichnyj-pasport-na-budynok/")
