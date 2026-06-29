from django.contrib import admin
from unfold.admin import ModelAdmin

from src.admin_base import ImagePreviewMixin, RichTextAdminMixin
from src.blog.models import BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(ImagePreviewMixin, RichTextAdminMixin, ModelAdmin):
    list_display = ("title", "slug", "language", "is_published", "published_at", "get_image_preview")
    list_filter = ("language", "is_published")
    search_fields = ("title", "slug", "excerpt")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("get_image_preview",)
    preview_field = "featured_image"
    rich_text_fields = ("body",)

    fieldsets = (
        (
            "Основне",
            {
                "fields": ("title", "slug", "language", "is_published", "published_at"),
                "classes": ["tab"],
            },
        ),
        (
            "Контент",
            {
                "fields": ("excerpt", "body"),
                "classes": ["tab"],
            },
        ),
        (
            "Зображення",
            {
                "fields": ("featured_image", "get_image_preview"),
                "classes": ["tab"],
            },
        ),
    )
