from django.test import RequestFactory, TestCase

from src.core.context_processors import _alternate_language_url, site_context


class AlternateLanguageUrlTests(TestCase):
    def test_home_to_ru_includes_hl_query(self):
        self.assertEqual(_alternate_language_url("/", "ru"), "/ru/?hl=ru")

    def test_home_from_ru_includes_hl_query(self):
        self.assertEqual(_alternate_language_url("/ru/", "ua"), "/?hl=ua")

    def test_inner_page_to_ru_includes_hl_query(self):
        self.assertEqual(
            _alternate_language_url("/contacts/", "ru"),
            "/ru/contacts/?hl=ru",
        )


class SiteContextTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_alternate_url_on_ua_home(self):
        request = self.factory.get("/")
        ctx = site_context(request)
        self.assertEqual(ctx["alternate_language_url"], "/ru/?hl=ru")
