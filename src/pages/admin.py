from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from src.cms.admin import PageBlockInline
from src.cms.models import PageSection
from src.pages.content_map import section_page_slug_for
from src.pages.models import StaticPage


@admin.register(StaticPage)
class StaticPageAdmin(ModelAdmin):
    list_display = ("title", "slug", "language", "is_published", "content_source_hint")
    list_filter = ("language", "is_published", "template_key")
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [PageBlockInline]
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

    @admin.display(description="Редагування текстів")
    def content_edit_hint(self, obj: StaticPage) -> str:
        if not obj or not obj.pk:
            return "Збережіть запис, щоб отримати посилання на секції з текстами."

        section_slug = section_page_slug_for(obj.slug)
        if section_slug:
            url = reverse("admin:cms_pagesection_changelist") + f"?page_slug__exact={section_slug}"
            count = PageSection.objects.filter(page_slug=section_slug).count()
            return format_html(
                "<p><strong>Тексти цієї сторінки — у розділі «Тексти сторінок».</strong> "
                'Поле «Body legacy» і блоки нижче для неї <strong>не використовуються</strong>.</p>'
                '<p><a class="button" href="{}">Відкрити тексти: {} ({} шт.)</a></p>'
                "<p>Меню та футер: фільтри «Шапка», «Футер», «Загальне».</p>",
                url,
                section_slug,
                count,
            )

        if obj.use_block_builder:
            return format_html(
                "<p>Ця сторінка збирається з <strong>Page blocks</strong> нижче або з поля «Body legacy».</p>"
            )

        return format_html(
            "<p>Редагуйте текст у полі «Body legacy» або увімкніть block builder.</p>"
        )

    @admin.display(description="Де редагувати контент")
    def content_source_hint(self, obj: StaticPage) -> str:
        if section_page_slug_for(obj.slug):
            return format_html(
                '<a href="{}?page_slug__exact={}">Тексти сторінок</a>',
                reverse("admin:cms_pagesection_changelist"),
                section_page_slug_for(obj.slug),
            )
        if obj.use_block_builder:
            return "Блоки / Body legacy"
        return "Body legacy"

    def get_inlines(self, request, obj=None):
        if obj and section_page_slug_for(obj.slug):
            return []
        return super().get_inlines(request, obj)
