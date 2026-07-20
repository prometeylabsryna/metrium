from django.contrib import admin
from unfold.admin import ModelAdmin

from src.admin_base import ImagePreviewMixin, ImageSizeHintMixin, RichTextAdminMixin
from src.blog.models import BlogPost
from src.cms.image_size_hints import HINT_BLOG


@admin.register(BlogPost)
class BlogPostAdmin(ImageSizeHintMixin, ImagePreviewMixin, RichTextAdminMixin, ModelAdmin):
    list_display = ("title", "slug", "language", "is_published", "published_at", "get_image_preview")
    list_filter = ("language", "is_published")
    search_fields = ("title", "slug", "excerpt")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("get_image_preview",)
    preview_field = "featured_image"
    rich_text_fields = ("body",)
    image_size_hints = {"featured_image": HINT_BLOG}

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
