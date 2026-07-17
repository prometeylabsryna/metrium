from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from src.cms.admin import PageBlockInline, PageSectionInline, SiteImageInline
from src.cms.models import PageSection, SiteImage
from src.cms.services import ensure_static_page_links, resolve_page_anchor
from src.pages.models import StaticPage


@admin.register(StaticPage)
class StaticPageAdmin(ModelAdmin):
    list_display = ("title", "slug", "language", "is_published", "content_source_hint")
    list_filter = ("language", "is_published", "template_key", "use_block_builder")
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("content_edit_hint",)

    fieldsets = (
        (
            "Основне",
            {
                "fields": ("title", "slug", "language", "is_published", "is_home"),
                "classes": ["tab"],
            },
        ),
        (
            "Шаблон",
            {
                "fields": ("template_key", "use_block_builder", "location"),
                "classes": ["tab"],
            },
        ),
        (
            "Контент",
            {
                "fields": ("content_edit_hint", "body_legacy", "published_at"),
                "classes": ["tab"],
            },
        ),
    )

    def _anchor_context(self, obj: StaticPage | None):
        """Повертає (anchor, is_anchor) — якірну StaticPage для slug і чи є нею obj."""
        if not obj or not obj.pk:
            return None, False
        ensure_static_page_links(obj)
        anchor = resolve_page_anchor(obj.slug)
        return anchor, bool(anchor and anchor.pk == obj.pk)

    @admin.display(description="Редагування текстів")
    def content_edit_hint(self, obj: StaticPage) -> str:
        if not obj or not obj.pk:
            return "Збережіть запис, щоб побачити тексти й зображення цієї сторінки."

        anchor, is_anchor = self._anchor_context(obj)
        parts: list[str] = []

        if is_anchor:
            sections = PageSection.objects.filter(content_type__isnull=False, object_id=obj.pk).count()
            images = SiteImage.objects.filter(content_type__isnull=False, object_id=obj.pk).count()
            if sections or images:
                parts.append(
                    format_html(
                        "<p><strong>Усі тексти й зображення цієї сторінки — нижче</strong>, "
                        "у вкладках «Тексти сторінки» ({} шт.) і «Зображення сторінки» ({} шт.). "
                        "Розкрийте вкладку і редагуйте прямо тут — окремо переходити нікуди не треба.</p>",
                        sections,
                        images,
                    )
                )
            else:
                parts.append(
                    format_html(
                        "<p>У цієї сторінки ще немає окремих текстових секцій. "
                        "За потреби додайте їх у вкладці «Тексти сторінки» нижче кнопкою «Add».</p>"
                    )
                )
        elif anchor:
            url = reverse("admin:pages_staticpage_change", args=[anchor.pk])
            parts.append(
                format_html(
                    "<p>Тексти для «{}» спільні з мовною версією <strong>«{} ({})»</strong> — "
                    "редагуйте їх там, поля UA/RU лежать в одному записі.</p>"
                    '<p><a class="button" href="{}">Відкрити «{}» ↗</a></p>',
                    obj.slug,
                    anchor.title,
                    anchor.get_language_display(),
                    url,
                    anchor.title,
                )
            )

        if obj.use_block_builder:
            parts.append(
                format_html("<p>Ця сторінка також збирається з <strong>Page blocks</strong> нижче.</p>")
            )
        elif not parts:
            parts.append(format_html("<p>Редагуйте текст у полі «Body legacy» або увімкніть block builder.</p>"))

        return format_html("".join(str(p) for p in parts))

    @admin.display(description="Де редагувати контент")
    def content_source_hint(self, obj: StaticPage) -> str:
        anchor, is_anchor = self._anchor_context(obj)
        if is_anchor and (
            PageSection.objects.filter(content_type__isnull=False, object_id=obj.pk).exists()
            or SiteImage.objects.filter(content_type__isnull=False, object_id=obj.pk).exists()
        ):
            return "Тексти й фото — нижче на сторінці"
        if anchor and not is_anchor:
            return format_html(
                '<a href="{}">Див. «{}»</a>',
                reverse("admin:pages_staticpage_change", args=[anchor.pk]),
                anchor.title,
            )
        if obj.use_block_builder:
            return "Блоки / Body legacy"
        return "Body legacy"

    def get_inlines(self, request, obj=None):
        inlines = []
        _, is_anchor = self._anchor_context(obj)
        if is_anchor:
            inlines += [PageSectionInline, SiteImageInline]
        if obj is None or obj.use_block_builder:
            inlines.append(PageBlockInline)
        return inlines

    def save_formset(self, request, form, formset, change):
        if formset.model in (PageSection, SiteImage):
            instances = formset.save(commit=False)
            for instance in instances:
                if not instance.page_slug:
                    instance.page_slug = form.instance.slug
                instance.save()
            formset.save_m2m()
        else:
            formset.save()
