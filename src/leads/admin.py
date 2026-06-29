from django.contrib import admin
from unfold.admin import ModelAdmin

from src.leads.models import LeadSubmission


@admin.register(LeadSubmission)
class LeadSubmissionAdmin(ModelAdmin):
    list_display = ("lead_type", "phone", "name", "page_title", "created_at")
    list_filter = ("lead_type", "channel")
    readonly_fields = ("payload", "created_at")
    search_fields = ("phone", "name", "page_title")
