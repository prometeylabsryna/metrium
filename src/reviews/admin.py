from django.contrib import admin
from unfold.admin import ModelAdmin

from src.reviews.models import Review


@admin.register(Review)
class ReviewAdmin(ModelAdmin):
    list_display = ["name", "rating", "is_published", "is_featured", "source", "published_at"]
    list_filter = ["is_published", "is_featured", "source", "rating"]
    list_editable = ["is_published", "is_featured"]
    search_fields = ["name", "text"]
    ordering = ["-published_at"]
    date_hierarchy = "published_at"

    fieldsets = (
        (
            "Відгук",
            {
                "fields": ("name", "text", "rating", "source", "published_at"),
                "classes": ["tab"],
            },
        ),
        (
            "Публікація",
            {
                "fields": ("is_published", "is_featured"),
                "classes": ["tab"],
            },
        ),
    )
