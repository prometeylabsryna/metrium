import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from src.migration.wp_sql_parser import (
    export_manifest_entries,
    load_wordpress_sql,
    parse_htaccess_gone,
)


class Command(BaseCommand):
    help = "Export SEO URL manifest and gone URLs from WordPress SQL dump."

    def add_arguments(self, parser):
        parser.add_argument(
            "--sql",
            type=str,
            default=settings.WORDPRESS_SQL_PATH,
            help="Path to metrium_prod.sql",
        )
        parser.add_argument(
            "--htaccess",
            type=str,
            default=settings.HTACCESS_PATH,
            help="Path to archive .htaccess",
        )
        parser.add_argument(
            "--output-dir",
            type=str,
            default=str(Path(settings.BASE_DIR) / "data" / "seo"),
            help="Output directory for manifest files",
        )

    def handle(self, *args, **options):
        sql_path = Path(options["sql"])
        htaccess_path = Path(options["htaccess"])
        output_dir = Path(options["output_dir"])
        output_dir.mkdir(parents=True, exist_ok=True)

        self.stdout.write(f"Loading {sql_path}...")
        data = load_wordpress_sql(sql_path)
        entries = export_manifest_entries(data)
        gone_paths = parse_htaccess_gone(htaccess_path)

        manifest_path = output_dir / "seo_manifest.json"
        gone_path = output_dir / "gone_410.json"
        redirects_path = output_dir / "redirects_301.json"

        manifest_path.write_text(
            json.dumps(entries, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        gone_path.write_text(
            json.dumps(gone_paths, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        redirects_path.write_text(
            json.dumps(
                [
                    {
                        "from": r.url_from,
                        "to": r.url_to,
                        "status": r.status,
                    }
                    for r in data.redirects
                ],
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Exported {len(entries)} URLs, {len(gone_paths)} gone (410), "
                f"{len(data.redirects)} DB redirects"
            )
        )
        self.stdout.write(f"  manifest: {manifest_path}")
        self.stdout.write(f"  gone_410: {gone_path}")
        self.stdout.write(f"  redirects: {redirects_path}")
