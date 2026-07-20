from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from src.admin_base import ImagePreviewMixin, ImageSizeHintMixin, SingletonAdminMixin
from src.cms.image_size_hints import HINT_HERO_DESKTOP, HINT_HERO_MOBILE, HINT_LOGO
from src.core.models import Office, SitePhone, SiteSettings


class SitePhoneInline(TabularInline):
    model = SitePhone
    extra = 0
    fields = ("display", "tel_href", "sort_order", "is_active")
    ordering = ("sort_order", "id")


@admin.register(SiteSettings)
class SiteSettingsAdmin(SingletonAdminMixin, ImageSizeHintMixin, ImagePreviewMixin, ModelAdmin):
    inlines = [SitePhoneInline]
    readonly_fields = ("get_logo_preview", "get_hero_desktop_preview", "get_hero_mobile_preview")
    preview_field = "logo"
    image_size_hints = {
        "logo": HINT_LOGO,
        "hero_image_desktop": HINT_HERO_DESKTOP,
        "hero_image_mobile": HINT_HERO_MOBILE,
    }

    fieldsets = (
        (
            "Брендинг",
            {
                "fields": (
                    "site_name",
                    "logo",
                    "get_logo_preview",
                    "logo_alt_ua",
                    "logo_alt_ru",
                ),
                "classes": ["tab"],
            },
        ),
        (
            "Контакти",
            {
                "fields": (
                    "email",
                    "region_label_ua",
                    "region_label_ru",
                    "schedule_header_ua",
                    "schedule_header_ru",
                    "schedule_weekdays_ua",
                    "schedule_weekdays_ru",
                    "schedule_saturday_ua",
                    "schedule_saturday_ru",
                    "schedule_sunday_ua",
                    "schedule_sunday_ru",
                ),
                "classes": ["tab"],
            },
        ),
        (
            "Месенджери та соцмережі",
            {
                "fields": ("telegram", "viber", "whatsapp", "instagram", "facebook"),
                "classes": ["tab"],
            },
        ),
        (
            "Головна — Hero",
            {
                "fields": (
                    "hero_image_desktop",
                    "get_hero_desktop_preview",
                    "hero_image_mobile",
                    "get_hero_mobile_preview",
                    "hero_title_ua",
                    "hero_title_ru",
                    "hero_subtitle_ua",
                    "hero_subtitle_ru",
                    "hero_form_title_ua",
                    "hero_form_title_ru",
                    "hero_form_text_ua",
                    "hero_form_text_ru",
                ),
                "classes": ["tab"],
            },
        ),
        (
            "Футер",
            {
                "fields": (
                    "footer_consult_title_ua",
                    "footer_consult_title_ru",
                    "footer_rights_ua",
                    "footer_rights_ru",
                    "privacy_url",
                    "privacy_label_ua",
                    "privacy_label_ru",
                ),
                "classes": ["tab"],
            },
        ),
    )

    @admin.display(description="Логотип")
    def get_logo_preview(self, obj: SiteSettings) -> str:
        return self.get_image_preview(obj)

    @admin.display(description="Hero (десктоп)")
    def get_hero_desktop_preview(self, obj: SiteSettings) -> str:
        self.preview_field = "hero_image_desktop"
        result = self.get_image_preview(obj)
        self.preview_field = "logo"
        return result

    @admin.display(description="Hero (мобільний)")
    def get_hero_mobile_preview(self, obj: SiteSettings) -> str:
        self.preview_field = "hero_image_mobile"
        result = self.get_image_preview(obj)
        self.preview_field = "logo"
        return result

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        from src.core.services import clear_site_cache

        clear_site_cache()


@admin.register(Office)
class OfficeAdmin(ModelAdmin):
    list_display = ["title", "city", "sort_order", "is_active", "is_main"]
    list_editable = ["sort_order", "is_active", "is_main"]
    ordering = ["sort_order"]
    search_fields = ["title", "city", "address"]
