from django.contrib import admin
from unfold.admin import ModelAdmin

from src.seo.models import SeoMetadata


@admin.register(SeoMetadata)
class SeoMetadataAdmin(ModelAdmin):
    list_display = ("seo_title", "content_type", "object_id", "robots_noindex")
    search_fields = ("seo_title", "seo_description")
    list_filter = ("robots_noindex",)
