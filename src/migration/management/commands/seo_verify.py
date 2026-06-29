import json
import re
from pathlib import Path
from urllib.parse import urljoin

import urllib.error
import urllib.request

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Verify Django site against exported SEO manifest."

    def add_arguments(self, parser):
        parser.add_argument(
            "--manifest",
            type=str,
            default="data/seo/seo_manifest.json",
        )
        parser.add_argument(
            "--gone",
            type=str,
            default="data/seo/gone_410.json",
        )
        parser.add_argument("--base-url", type=str, default="http://127.0.0.1:8000")
        parser.add_argument("--sample", type=int, default=50)

    def handle(self, *args, **options):
        manifest_path = Path(options["manifest"])
        gone_path = Path(options["gone"])
        base_url = options["base_url"].rstrip("/") + "/"

        if not manifest_path.exists():
            self.stderr.write(f"Manifest not found: {manifest_path}")
            return

        entries = json.loads(manifest_path.read_text(encoding="utf-8"))
        gone_paths = json.loads(gone_path.read_text(encoding="utf-8")) if gone_path.exists() else []

        ok = 0
        fail = 0
        sample = entries[: options["sample"]]

        for entry in sample:
            url = urljoin(base_url, entry["path"].lstrip("/"))
            try:
                with urllib.request.urlopen(url, timeout=10) as resp:
                    if resp.status == 200:
                        ok += 1
                    else:
                        fail += 1
                        self.stderr.write(f"FAIL {entry['path']}: status {resp.status}")
            except Exception as exc:
                fail += 1
                self.stderr.write(f"FAIL {entry['path']}: {exc}")

        gone_ok = 0
        gone_fail = 0
        for path in gone_paths[:20]:
            url = urljoin(base_url, path.lstrip("/"))
            try:
                with urllib.request.urlopen(url, timeout=10) as resp:
                    if resp.status == 410:
                        gone_ok += 1
                    else:
                        gone_fail += 1
            except urllib.error.HTTPError as exc:
                if exc.code == 410:
                    gone_ok += 1
                else:
                    gone_fail += 1
            except Exception:
                gone_fail += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Live URLs: {ok} OK, {fail} FAIL (sample {len(sample)}/{len(entries)})"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(f"Gone URLs: {gone_ok} OK, {gone_fail} FAIL (sample 20)")
        )

        sitemap_url = urljoin(base_url, "sitemap.xml")
        try:
            with urllib.request.urlopen(sitemap_url, timeout=10) as resp:
                body = resp.read().decode("utf-8", errors="replace")
                loc_count = len(re.findall(r"<loc>", body))
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Sitemap index: {loc_count} sections at {sitemap_url}"
                    )
                )
        except Exception as exc:
            self.stderr.write(f"Sitemap check failed: {exc}")

        if fail == 0 and gone_fail == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    "Cutover gate: PASS for sampled URLs. "
                    "Rollback: revert DNS A-record to WordPress host if 404/410 spikes."
                )
            )
        else:
            self.stderr.write(
                "Cutover gate: FAIL — fix regressions before DNS switch."
            )
