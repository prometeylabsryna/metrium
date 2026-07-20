from __future__ import annotations

import re
from pathlib import Path

from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.files import File
from django.core.management.base import BaseCommand

from src.cms.models import SiteImage
from src.cms.page_labels import page_label
from src.cms.services import clear_image_cache, link_all_page_content
from src.cms.site_images_manifest import DOC_EXAMPLE_IMAGES, HERO_IMAGES, MANUAL_IMAGES
from src.cms.text_keys import page_slug_from_template_path

STATIC_IMAGE_RE = re.compile(r"\{%\s*static\s+['\"](images/kata/[^'\"]+)['\"]\s*%\}")


class Command(BaseCommand):
    help = "Імпортує зображення з шаблонів у SiteImage для редагування в адмінці"

    def add_arguments(self, parser):
        parser.add_argument(
            "--import-files",
            action="store_true",
            help="Скопіювати файли з static/ у media/ для нових записів",
        )
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Перезаписати fallback-шляхи для існуючих записів",
        )

    def handle(self, *args, **options):
        import_files = options["import_files"]
        overwrite = options["overwrite"]
        created = 0
        updated = 0
        skipped = 0

        seen: set[tuple[str, str]] = set()
        items: list[dict] = []

        for page_slug, (desktop, mobile) in HERO_IMAGES.items():
            items.append(
                {
                    "page_slug": page_slug,
                    "image_key": "hero",
                    "label": f"Hero: {page_label(page_slug)}",
                    "fallback_static": desktop,
                    "fallback_static_mobile": mobile,
                    "sort_order": 0,
                }
            )

        for page_slug, (static_path, alt_ua, alt_ru) in DOC_EXAMPLE_IMAGES.items():
            items.append(
                {
                    "page_slug": page_slug,
                    "image_key": "doc.example",
                    "label": "Зразок документа",
                    "fallback_static": static_path,
                    "image_alt_ua": alt_ua,
                    "image_alt_ru": alt_ru,
                }
            )

        items.extend(MANUAL_IMAGES)

        templates_dir = Path(settings.BASE_DIR) / "templates"
        for path in sorted(templates_dir.rglob("*.html")):
            rel = str(path.relative_to(templates_dir))
            page_slug = page_slug_from_template_path(rel)
            if page_slug in ("header", "footer", "global") and "partials" in rel:
                page_slug = page_slug_from_template_path(rel)

            static_paths = STATIC_IMAGE_RE.findall(path.read_text(encoding="utf-8"))
            for index, static_path in enumerate(dict.fromkeys(static_paths)):
                filename = Path(static_path).name
                stem = Path(static_path).stem
                if stem.endswith("-mob"):
                    continue
                if page_slug in HERO_IMAGES and static_path in HERO_IMAGES[page_slug]:
                    continue
                if any(item.get("fallback_static") == static_path for item in items):
                    continue

                image_key = f"static.{stem}"
                if (page_slug, image_key) in seen:
                    continue
                items.append(
                    {
                        "page_slug": page_slug,
                        "image_key": image_key,
                        "label": filename,
                        "fallback_static": static_path,
                        "sort_order": index,
                    }
                )

        for data in items:
            key = (data["page_slug"], data["image_key"])
            if key in seen:
                continue
            seen.add(key)
            action = self._upsert_image(data, import_files, overwrite)
            if action == "created":
                created += 1
            elif action == "updated":
                updated += 1
            else:
                skipped += 1

        clear_image_cache()
        linked = link_all_page_content()
        self.stdout.write(
            self.style.SUCCESS(
                f"Готово: створено {created}, оновлено {updated}, пропущено {skipped}"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Привʼязка до сторінок: {linked['pages']} сторінок, "
                f"{linked['sections']} текстів, {linked['images']} зображень"
            )
        )

    def _upsert_image(self, data: dict, import_files: bool, overwrite: bool) -> str:
        defaults = {
            "label": data["label"],
            "fallback_static": data.get("fallback_static", ""),
            "fallback_static_mobile": data.get("fallback_static_mobile", ""),
            "image_alt_ua": data.get("image_alt_ua", ""),
            "image_alt_ru": data.get("image_alt_ru", ""),
            "sort_order": data.get("sort_order", 0),
            "is_active": True,
        }
        obj, created = SiteImage.objects.get_or_create(
            page_slug=data["page_slug"],
            image_key=data["image_key"],
            defaults=defaults,
        )
        if created:
            if import_files:
                self._import_static_files(obj)
            return "created"

        if overwrite:
            for field, value in defaults.items():
                setattr(obj, field, value)
            obj.save()
            return "updated"

        changed = False
        for field in ("label", "fallback_static", "fallback_static_mobile", "image_alt_ua", "image_alt_ru"):
            value = defaults.get(field, "")
            if value and not getattr(obj, field):
                setattr(obj, field, value)
                changed = True
        # Оновити технічні назви Hero: slug → Hero: Людська назва
        new_label = defaults.get("label", "")
        if (
            obj.image_key == "hero"
            and new_label.startswith("Hero: ")
            and obj.label.startswith("Hero: ")
            and obj.label != new_label
            and obj.label.replace("Hero: ", "") == obj.page_slug
        ):
            obj.label = new_label
            changed = True
        if changed:
            obj.save()
            return "updated"
        return "skipped"

    def _import_static_files(self, obj: SiteImage) -> None:
        if obj.fallback_static and not obj.image:
            self._copy_static_to_field(obj, "image", obj.fallback_static)
        if obj.fallback_static_mobile and not obj.image_mobile:
            self._copy_static_to_field(obj, "image_mobile", obj.fallback_static_mobile)
        obj.save()

    def _copy_static_to_field(self, obj: SiteImage, field_name: str, static_path: str) -> None:
        found = finders.find(static_path)
        if not found:
            return
        with open(found, "rb") as handle:
            getattr(obj, field_name).save(Path(static_path).name, File(handle), save=False)
