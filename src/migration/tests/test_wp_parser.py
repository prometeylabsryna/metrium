from pathlib import Path

from django.conf import settings
from django.test import TestCase

from src.migration.wp_sql_parser import build_url_path, parse_htaccess_gone


class WpParserTests(TestCase):
    def test_front_page_url(self):
        self.assertEqual(build_url_path("golovna", "ua", "page", wp_id=9), "/")

    def test_htaccess_gone_count(self):
        paths = parse_htaccess_gone(Path(settings.HTACCESS_PATH))
        self.assertEqual(len(paths), 946)
