from django.contrib import admin
from unfold.admin import ModelAdmin

from src.redirects.models import RedirectRule


@admin.register(RedirectRule)
class RedirectRuleAdmin(ModelAdmin):
    list_display = ("source_path", "status_code", "target_url", "source", "is_active")
    list_filter = ("status_code", "source", "is_active")
    search_fields = ("source_path", "target_url")
