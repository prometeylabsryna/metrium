from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from src.blog.models import BlogPost
from src.cms.models import PageBlock
from src.i18n.models import Language
from src.migration.acf_parser import parse_acf_blocks
from src.migration.wp_sql_parser import (
    FRONT_PAGE_IDS,
    build_url_path,
    load_wordpress_sql,
    parse_htaccess_gone,
)
from src.pages.models import StaticPage
from src.pages.ru_prefix import strip_ru_slug_prefix
from src.redirects.middleware import RedirectMiddleware
from src.redirects.models import RedirectRule
from src.seo.models import SeoMetadata


class Command(BaseCommand):
    help = "Import WordPress content from SQL dump into Django models."

    def add_arguments(self, parser):
        parser.add_argument("--sql", type=str, default=settings.WORDPRESS_SQL_PATH)
        parser.add_argument("--htaccess", type=str, default=settings.HTACCESS_PATH)
        parser.add_argument("--clear", action="store_true", help="Clear existing data")

    @transaction.atomic
    def handle(self, *args, **options):
        sql_path = Path(options["sql"])
        htaccess_path = Path(options["htaccess"])

        if options["clear"]:
            PageBlock.objects.all().delete()
            SeoMetadata.objects.all().delete()
            BlogPost.objects.all().delete()
            StaticPage.objects.all().delete()
            RedirectRule.objects.all().delete()

        self.stdout.write(f"Loading {sql_path}...")
        data = load_wordpress_sql(sql_path)

        post_to_group: dict[int, int] = {}
        group_map: dict[int, dict[str, int]] = {}
        for term_id, group in data.translation_groups.items():
            for lang, pid in group.items():
                post_to_group[pid] = term_id
            group_map[term_id] = group

        page_ct = ContentType.objects.get_for_model(StaticPage)
        blog_ct = ContentType.objects.get_for_model(BlogPost)
        wp_to_page: dict[int, StaticPage] = {}
        wp_to_blog: dict[int, BlogPost] = {}

        for post_id, post in data.posts.items():
            if post.post_status != "publish":
                continue
            language = data.post_language.get(post_id, Language.UA)
            group_id = post_to_group.get(post_id)
            template = data.postmeta.get(post_id, {}).get("_wp_page_template", "")
            location = data.postmeta.get(post_id, {}).get("location", "")
            published = self._parse_dt(post.post_date)

            if post.post_type == "page":
                raw_slug = post.post_name or f"page-{post_id}"
                slug, was_ru_prefixed = strip_ru_slug_prefix(raw_slug)
                if was_ru_prefixed:
                    language = Language.RU
                obj, _ = StaticPage.objects.update_or_create(
                    wp_id=post_id,
                    defaults={
                        "slug": slug,
                        "title": post.post_title,
                        "language": language,
                        "translation_group_id": group_id,
                        "template_key": template,
                        "use_block_builder": True,
                        "is_published": True,
                        "is_home": post_id in FRONT_PAGE_IDS,
                        "location": location,
                        "body_legacy": post.post_content,
                        "published_at": published,
                    },
                )
                wp_to_page[post_id] = obj
                if was_ru_prefixed:
                    RedirectRule.objects.update_or_create(
                        source_path=f"/{raw_slug}",
                        defaults={
                            "target_url": f"/ru/{slug}/",
                            "status_code": 301,
                            "is_active": True,
                            "source": "manual",
                        },
                    )
                self._import_blocks(obj, page_ct, data.postmeta.get(post_id, {}))
                self._import_seo(obj, post_id, data)

            elif post.post_type == "blogs":
                obj, _ = BlogPost.objects.update_or_create(
                    wp_id=post_id,
                    defaults={
                        "slug": post.post_name,
                        "title": post.post_title,
                        "language": language,
                        "translation_group_id": group_id,
                        "excerpt": post.post_excerpt,
                        "body": post.post_content,
                        "is_published": True,
                        "published_at": published,
                    },
                )
                wp_to_blog[post_id] = obj
                self._import_seo(obj, post_id, data)

        self._import_redirects(data, htaccess_path)
        self._import_home_aliases(wp_to_page)
        RedirectMiddleware.clear_cache()

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {len(wp_to_page)} pages, {len(wp_to_blog)} blog posts, "
                f"{RedirectRule.objects.count()} redirect rules"
            )
        )

    def _parse_priority(self, raw: str | None):
        if not raw:
            return None
        try:
            return float(raw)
        except (TypeError, ValueError):
            return None

    def _parse_dt(self, raw: str):
        if not raw or raw.startswith("0000"):
            return timezone.now()
        try:
            dt = datetime.strptime(raw, "%Y-%m-%d %H:%M:%S")
            return timezone.make_aware(dt) if timezone.is_naive(dt) else dt
        except ValueError:
            return timezone.now()

    def _import_blocks(self, page, content_type, postmeta: dict):
        PageBlock.objects.filter(content_type=content_type, object_id=page.pk).delete()
        for block_data in parse_acf_blocks(postmeta):
            PageBlock.objects.create(
                content_type=content_type,
                object_id=page.pk,
                kind=block_data["kind"],
                sort_order=block_data.get("sort_order", 0),
                heading=block_data.get("heading", ""),
                body=block_data.get("body", ""),
                extra_data=block_data.get("extra_data", {}),
            )

    def _import_seo(self, obj, wp_post_id: int, data):
        seo = data.seo.get(wp_post_id)
        if not seo:
            return
        SeoMetadata.objects.update_or_create(
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.pk,
            defaults={
                "seo_title": seo.title,
                "seo_description": seo.description,
                "canonical_url": seo.canonical_url,
                "robots_noindex": seo.robots_noindex,
                "robots_nofollow": seo.robots_nofollow,
                "og_title": seo.og_title,
                "og_description": seo.og_description,
                "og_image_url": seo.og_image_url,
                "schema_json": seo.schema,
                "sitemap_priority": self._parse_priority(seo.priority),
                "sitemap_changefreq": seo.frequency or "",
            },
        )

    def _import_home_aliases(self, wp_to_page: dict[int, StaticPage]) -> None:
        for page in wp_to_page.values():
            if not page.is_home:
                continue
            slug_path = f"/{page.slug}/" if page.language == Language.UA else f"/ru/{page.slug}/"
            home_path = page.get_absolute_url()
            if slug_path != home_path:
                RedirectRule.objects.update_or_create(
                    source_path=slug_path.rstrip("/") or "/",
                    defaults={
                        "target_url": home_path,
                        "status_code": 301,
                        "source": "home-alias",
                    },
                )

    def _import_redirects(self, data, htaccess_path: Path):
        for path in parse_htaccess_gone(htaccess_path):
            norm = path.rstrip("/") or "/"
            RedirectRule.objects.update_or_create(
                source_path=norm,
                defaults={"status_code": 410, "target_url": "", "source": "htaccess"},
            )
        for redirect in data.redirects:
            source = "/" + redirect.url_from.strip("/")
            target = redirect.url_to
            if target.isdigit():
                wp_post = data.posts.get(int(target))
                if wp_post:
                    lang = data.post_language.get(int(target), Language.UA)
                    target = build_url_path(wp_post.post_name, lang, wp_post.post_type)
                else:
                    continue
            elif not target.startswith("/") and not target.startswith("http"):
                target = "/" + target
            RedirectRule.objects.update_or_create(
                source_path=source.rstrip("/") or "/",
                defaults={
                    "target_url": target,
                    "status_code": redirect.status,
                    "source": "eps",
                },
            )
