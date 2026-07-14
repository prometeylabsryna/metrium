from django.core.management.base import BaseCommand
from django.db import transaction

from src.i18n.models import Language
from src.pages.models import StaticPage
from src.pages.ru_prefix import strip_ru_slug_prefix
from src.redirects.middleware import RedirectMiddleware
from src.redirects.models import RedirectRule


class Command(BaseCommand):
    help = (
        "Normalize legacy WordPress RU pages: strip ru- slug prefix, "
        "set language=ru, add 301 redirects, link UA/RU translation pairs."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show changes without writing to the database",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        pages = list(
            StaticPage.objects.filter(slug__startswith="ru-").order_by("slug")
        )
        if not pages:
            self.stdout.write(self.style.SUCCESS("No ru-* pages to normalize."))
            return

        updated = 0
        redirects = 0
        linked = 0
        skipped = 0

        for page in pages:
            new_slug, prefixed = strip_ru_slug_prefix(page.slug)
            if not prefixed or not new_slug:
                skipped += 1
                continue

            conflict = (
                StaticPage.objects.filter(slug=new_slug, language=Language.RU)
                .exclude(pk=page.pk)
                .exists()
            )
            if conflict:
                self.stdout.write(
                    self.style.WARNING(
                        f"Skip {page.slug}: RU page with slug={new_slug} already exists"
                    )
                )
                skipped += 1
                continue

            old_path = f"/{page.slug}"
            new_path = f"/ru/{new_slug}/"
            self.stdout.write(f"{page.slug} ({page.language}) -> {new_slug} (ru)  {old_path} => {new_path}")

            if not dry_run:
                page.slug = new_slug
                page.language = Language.RU
                page.save(update_fields=["slug", "language", "updated_at"])

                RedirectRule.objects.update_or_create(
                    source_path=old_path,
                    defaults={
                        "target_url": new_path,
                        "status_code": 301,
                        "is_active": True,
                        "source": "manual",
                    },
                )
                redirects += 1

                ua = StaticPage.objects.filter(
                    slug=new_slug,
                    language=Language.UA,
                    is_published=True,
                ).first()
                if ua:
                    group_id = page.translation_group_id or ua.translation_group_id
                    if not group_id:
                        group_id = page.pk
                    if page.translation_group_id != group_id:
                        page.translation_group_id = group_id
                        page.save(update_fields=["translation_group_id", "updated_at"])
                    if ua.translation_group_id != group_id:
                        ua.translation_group_id = group_id
                        ua.save(update_fields=["translation_group_id", "updated_at"])
                    linked += 1

            updated += 1

        if dry_run:
            transaction.set_rollback(True)
            self.stdout.write(
                self.style.WARNING(
                    f"Dry run: would update {updated} pages, skip {skipped}"
                )
            )
            return

        RedirectMiddleware.clear_cache()
        self.stdout.write(
            self.style.SUCCESS(
                f"Updated {updated} pages, {redirects} redirects, "
                f"{linked} translation pairs linked, skipped {skipped}"
            )
        )
