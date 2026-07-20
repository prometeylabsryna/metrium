import re

from django.contrib import admin
from django.utils.html import format_html, strip_tags
from unfold.admin import ModelAdmin

from src.admin_base import ImagePreviewMixin, RichTextAdminMixin
from src.cms.models import HomeServiceCard, HomeStatItem, HomeWhyItem, PageBlock, PageSection, SiteImage
from src.cms.page_labels import page_label, page_public_url
from src.cms.services import clear_image_cache, clear_section_cache


@admin.register(PageBlock)
class PageBlockAdmin(ImagePreviewMixin, RichTextAdminMixin, ModelAdmin):
    list_display = ("kind", "sort_order", "is_visible", "content_type", "object_id", "get_image_preview")
    list_filter = ("kind", "is_visible")
    search_fields = ("heading", "body", "css_anchor")
    readonly_fields = ("get_image_preview",)
    rich_text_fields = ("body",)

    fieldsets = (
        (
            "Основне",
            {
                "fields": ("kind", "sort_order", "is_visible", "css_anchor", "heading"),
                "classes": ["tab"],
            },
        ),
        (
            "Текст і кнопка",
            {
                "fields": ("body", "button_text", "button_url"),
                "classes": ["tab"],
            },
        ),
        (
            "Зображення",
            {
                "fields": ("image", "get_image_preview", "image_alt"),
                "classes": ["tab"],
            },
        ),
        (
            "Додаткові дані",
            {
                "fields": ("extra_data",),
                "classes": ["tab"],
            },
        ),
    )


@admin.register(PageSection)
class PageSectionAdmin(ImagePreviewMixin, RichTextAdminMixin, ModelAdmin):
    list_before_template = "admin/cms/pagesection_changelist_before.html"
    list_display = (
        "label",
        "get_page_name",
        "get_text_preview",
        "has_media",
        "is_active",
    )
    list_filter = ("page_slug", "is_active")
    search_fields = ("label", "section_key", "text_ua", "text_ru", "body_ua", "body_ru")
    list_per_page = 40
    readonly_fields = (
        "admin_guide",
        "site_preview_link",
        "get_image_preview",
        "get_icon_preview",
    )
    rich_text_fields = ("body_ua", "body_ru")
    ordering = ("page_slug", "sort_order", "section_key")

    fieldsets = (
        (
            "Довідка",
            {
                "fields": ("admin_guide", "site_preview_link"),
                "classes": ["tab"],
            },
        ),
        (
            "Де показується",
            {
                "fields": ("page_slug", "label", "is_active"),
                "description": "Оберіть сторінку сайту, до якої належить цей текст.",
                "classes": ["tab"],
            },
        ),
        (
            "Текст українською",
            {
                "fields": ("text_ua", "body_ua"),
                "description": "«Текст» — для заголовків і коротких рядків. «HTML» — для абзаців, списків і FAQ.",
                "classes": ["tab"],
            },
        ),
        (
            "Текст російською",
            {
                "fields": ("text_ru", "body_ru"),
                "classes": ["tab"],
            },
        ),
        (
            "Зображення",
            {
                "fields": (
                    "image",
                    "get_image_preview",
                    "image_alt_ua",
                    "image_alt_ru",
                    "icon",
                    "get_icon_preview",
                    "url",
                ),
                "description": "Завантажте файл — він зʼявиться на сайті там, де передбачено шаблоном (наприклад, банер послуги).",
                "classes": ["tab"],
            },
        ),
        (
            "Службове",
            {
                "fields": ("section_key", "sort_order"),
                "classes": ["tab"],
            },
        ),
    )

    @admin.display(description="Сторінка")
    def get_page_name(self, obj: PageSection) -> str:
        return page_label(obj.page_slug)

    @admin.display(description="Текст (UA)")
    def get_text_preview(self, obj: PageSection) -> str:
        raw = obj.text_ua or obj.body_ua or ""
        clean = re.sub(r"\s+", " ", strip_tags(raw)).strip()
        if not clean:
            return "—"
        if len(clean) > 70:
            return f"{clean[:69]}…"
        return clean

    @admin.display(description="Фото", boolean=True)
    def has_media(self, obj: PageSection) -> bool:
        return bool(obj.image or obj.icon)

    @admin.display(description="Підказка")
    def admin_guide(self, obj: PageSection) -> str:
        if not obj or not obj.pk:
            return (
                "Після збереження тут зʼявиться посилання на сторінку сайту. "
                "Змінюйте поля «Текст (UA/RU)» або «HTML» — зміни одразу потрапляють на сайт."
            )
        return format_html(
            "<ol style='margin:0;padding-left:1.2rem;line-height:1.6;'>"
            "<li>Короткі рядки — поле <strong>Текст (UA/RU)</strong>.</li>"
            "<li>Абзаци, списки, FAQ — поле <strong>HTML / довгий текст</strong> (редактор).</li>"
            "<li>Банер або іконка — вкладка <strong>Зображення</strong>.</li>"
            "<li>Порожнє поле = на сайті лишається текст за замовчуванням з шаблону.</li>"
            "</ol>"
        )

    @admin.display(description="Переглянути на сайті")
    def site_preview_link(self, obj: PageSection) -> str:
        if not obj or not obj.pk:
            return "—"
        url = page_public_url(obj.page_slug)
        return format_html(
            '<a href="{}" target="_blank" rel="noopener">Відкрити сторінку «{}» ↗</a>',
            url,
            page_label(obj.page_slug),
        )

    @admin.display(description="Іконка")
    def get_icon_preview(self, obj: PageSection) -> str:
        self.preview_field = "icon"
        result = self.get_image_preview(obj)
        self.preview_field = "image"
        return result

    def get_readonly_fields(self, request, obj=None):
        readonly = list(self.readonly_fields)
        if obj:
            readonly.append("section_key")
        return readonly

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        page_slug = request.GET.get("page_slug__exact")
        if page_slug:
            extra_context["filtered_page_label"] = page_label(page_slug)
            extra_context["filtered_page_url"] = page_public_url(page_slug)
        return super().changelist_view(request, extra_context)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        clear_section_cache(obj.page_slug, obj.section_key)


@admin.register(SiteImage)
class SiteImageAdmin(ImagePreviewMixin, ModelAdmin):
    list_display = (
        "label",
        "get_page_name",
        "image_key",
        "has_uploaded_image",
        "is_active",
    )
    list_filter = ("page_slug", "is_active")
    search_fields = ("label", "image_key", "image_alt_ua", "image_alt_ru", "fallback_static")
    list_per_page = 40
    readonly_fields = ("get_image_preview", "get_mobile_preview", "site_preview_link")
    ordering = ("page_slug", "sort_order", "image_key")

    fieldsets = (
        (
            "Де показується",
            {
                "fields": ("page_slug", "label", "is_active", "site_preview_link"),
                "classes": ["tab"],
            },
        ),
        (
            "Зображення",
            {
                "fields": (
                    "image",
                    "get_image_preview",
                    "image_mobile",
                    "get_mobile_preview",
                    "image_alt_ua",
                    "image_alt_ru",
                ),
                "classes": ["tab"],
            },
        ),
        (
            "Fallback (якщо файл не завантажено)",
            {
                "fields": ("fallback_static", "fallback_static_mobile"),
                "description": "Шлях від static/, наприклад images/kata/kvartiry.webp",
                "classes": ["tab"],
            },
        ),
        (
            "Службове",
            {
                "fields": ("image_key", "sort_order"),
                "classes": ["tab"],
            },
        ),
    )

    @admin.display(description="Сторінка")
    def get_page_name(self, obj: SiteImage) -> str:
        return page_label(obj.page_slug)

    @admin.display(description="Файл", boolean=True)
    def has_uploaded_image(self, obj: SiteImage) -> bool:
        return bool(obj.image or obj.image_mobile)

    @admin.display(description="Переглянути на сайті")
    def site_preview_link(self, obj: SiteImage) -> str:
        if not obj or not obj.pk:
            return "—"
        url = page_public_url(obj.page_slug)
        return format_html(
            '<a href="{}" target="_blank" rel="noopener">Відкрити сторінку «{}» ↗</a>',
            url,
            page_label(obj.page_slug),
        )

    @admin.display(description="Мобільне")
    def get_mobile_preview(self, obj: SiteImage) -> str:
        self.preview_field = "image_mobile"
        result = self.get_image_preview(obj)
        self.preview_field = "image"
        return result

    def get_readonly_fields(self, request, obj=None):
        readonly = list(self.readonly_fields)
        if obj:
            readonly.append("image_key")
        return readonly

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        clear_image_cache(obj.page_slug, obj.image_key)


@admin.register(HomeServiceCard)
class HomeServiceCardAdmin(ImagePreviewMixin, ModelAdmin):
    list_display = ("title_ua", "sort_order", "is_active", "get_image_preview")
    list_editable = ("sort_order", "is_active")
    search_fields = ("title_ua", "title_ru")
    readonly_fields = ("get_image_preview",)
    preview_field = "icon"

    fieldsets = (
        (
            "Контент",
            {
                "fields": (
                    "title_ua",
                    "title_ru",
                    "description_ua",
                    "description_ru",
                    "url",
                    "sort_order",
                    "is_active",
                ),
                "classes": ["tab"],
            },
        ),
        (
            "Іконка",
            {
                "fields": ("icon", "get_image_preview"),
                "classes": ["tab"],
            },
        ),
    )


@admin.register(HomeWhyItem)
class HomeWhyItemAdmin(ImagePreviewMixin, ModelAdmin):
    list_display = ("title_ua", "sort_order", "is_active", "get_image_preview")
    list_editable = ("sort_order", "is_active")
    readonly_fields = ("get_image_preview",)
    preview_field = "icon"


@admin.register(HomeStatItem)
class HomeStatItemAdmin(ModelAdmin):
    list_display = ("value", "label_ua", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
