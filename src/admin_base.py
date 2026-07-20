from __future__ import annotations

from django.contrib import admin
from django.http import HttpRequest
from django.shortcuts import redirect
from django.utils.html import format_html
from tinymce.widgets import TinyMCE


class ImageSizeHintMixin:
    """Підказки рекомендованого розміру для ImageField у адмінці."""

    image_size_hints: dict[str, str] = {}

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if formfield is not None and db_field.name in getattr(self, "image_size_hints", {}):
            formfield.help_text = self.image_size_hints[db_field.name]
        return formfield


class SingletonAdminMixin:
    def has_add_permission(self, request: HttpRequest) -> bool:
        return not self.model.objects.exists()

    def has_delete_permission(self, request: HttpRequest, obj=None) -> bool:
        return False

    def changelist_view(self, request: HttpRequest, extra_context=None):
        instance = self.model.objects.first()
        if instance:
            return redirect(f"/admin/{instance._meta.app_label}/{instance._meta.model_name}/{instance.pk}/change/")
        return super().changelist_view(request, extra_context)


class ImagePreviewMixin:
    preview_field = "image"
    preview_size = 120

    def get_image_preview(self, obj) -> str:
        image = getattr(obj, self.preview_field, None)
        if not image:
            return "—"
        return format_html(
            '<img src="{}" style="max-height:{}px;border-radius:8px;object-fit:cover;" />',
            image.url,
            self.preview_size,
        )

    get_image_preview.short_description = "Превʼю"


class RichTextAdminMixin:
    rich_text_fields: tuple[str, ...] = ()

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name in self.rich_text_fields:
            kwargs["widget"] = TinyMCE(
                attrs={"cols": 80, "rows": 20},
                mce_attrs={
                    "plugins": "link lists table code",
                    "toolbar": "undo redo | bold italic underline | bullist numlist | link | removeformat",
                    "menubar": False,
                    "statusbar": False,
                    "language": "uk",
                },
            )
        return super().formfield_for_dbfield(db_field, request, **kwargs)
