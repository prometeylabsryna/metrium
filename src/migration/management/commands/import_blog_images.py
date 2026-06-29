import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from src.blog.models import BlogPost
from src.migration.wp_sql_parser import load_wordpress_sql


class Command(BaseCommand):
    help = "Import blog featured images from WordPress uploads archive."

    def add_arguments(self, parser):
        parser.add_argument("--sql", type=str, default=settings.WORDPRESS_SQL_PATH)
        parser.add_argument("--force", action="store_true", help="Overwrite existing images")

    def handle(self, *args, **options):
        sql_path = Path(options["sql"])
        uploads_root = Path(settings.WP_UPLOADS_ROOT)
        media_blog = Path(settings.MEDIA_ROOT) / "blog"
        media_blog.mkdir(parents=True, exist_ok=True)

        self.stdout.write(f"Loading {sql_path}...")
        data = load_wordpress_sql(sql_path)

        wp_to_post = {
            post.wp_id: post
            for post in BlogPost.objects.exclude(wp_id__isnull=True)
        }

        imported = 0
        skipped = 0
        missing = 0

        for wp_id, wp_post in data.posts.items():
            if wp_post.post_type != "blogs" or wp_post.post_status != "publish":
                continue

            post = wp_to_post.get(wp_id)
            if not post:
                continue

            if post.featured_image and not options["force"]:
                skipped += 1
                continue

            thumb_id = data.postmeta.get(wp_id, {}).get("_thumbnail_id")
            if not thumb_id:
                missing += 1
                continue

            rel_path = data.attachment_paths.get(int(thumb_id))
            if not rel_path:
                missing += 1
                continue

            src = uploads_root / rel_path
            if not src.is_file():
                missing += 1
                self.stdout.write(self.style.WARNING(f"File not found: {src}"))
                continue

            dest_name = f"{post.slug}{src.suffix.lower()}"
            dest = media_blog / dest_name

            if not dest.exists() or options["force"]:
                shutil.copy2(src, dest)

            if post.featured_image.name != f"blog/{dest_name}":
                post.featured_image.name = f"blog/{dest_name}"
                post.save(update_fields=["featured_image"])

            imported += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done: {imported} imported, {skipped} skipped, {missing} missing"
            )
        )
