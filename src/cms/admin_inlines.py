"""Інлайни для хабу редагування сторінки (StaticPage) — блоки як на сайті."""

from __future__ import annotations

from django import forms
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericInlineModelAdmin, GenericStackedInline, GenericTabularInline
from django.contrib.contenttypes.models import ContentType
from django.forms.models import BaseModelFormSet
from django.utils.html import format_html

from src.cms.image_size_hints import apply_site_image_hints
from src.cms.models import PageBlock, PageSection, SiteImage
from src.cms.services import ensure_static_page_links, resolve_page_anchor
from src.i18n.models import Language

try:
    from unfold.overrides import FORMFIELD_OVERRIDES_INLINE
except ImportError:
    FORMFIELD_OVERRIDES_INLINE = {}


class UnfoldGenericStackedInline(GenericStackedInline):
    formfield_overrides = FORMFIELD_OVERRIDES_INLINE
    readonly_preprocess_fields: dict = {}


class _AnchoredGenericFormSetMixin:
    def get_queryset(self):
        instance = self.instance
        if not instance or not instance.pk:
            return self.model.objects.none()

        ensure_static_page_links(instance)
        anchor = resolve_page_anchor(instance.slug)
        if not anchor:
            return self.model.objects.none()

        ct = ContentType.objects.get_for_model(instance.__class__)
        # block_title першим — однакові блоки підряд (інакше ifchanged плодить дублікати)
        return self.model.objects.filter(content_type=ct, object_id=anchor.pk).order_by(
            "block_title", "sort_order", "id"
        )

    def save_new(self, form, commit=True):
        instance = self.instance
        ensure_static_page_links(instance)
        anchor = resolve_page_anchor(instance.slug) or instance
        ct = ContentType.objects.get_for_model(instance.__class__)
        setattr(form.instance, self.ct_field.get_attname(), ct.pk)
        setattr(form.instance, self.ct_fk_field.get_attname(), anchor.pk)
        if not form.instance.page_slug:
            form.instance.page_slug = "home" if instance.is_home else instance.slug
        return BaseModelFormSet.save_new(self, form, commit=commit)


def _make_anchored_formset(base_formset, order_by: tuple[str, ...]):
    class AnchoredFormSet(_AnchoredGenericFormSetMixin, base_formset):
        _order_by = order_by

    return AnchoredFormSet


class PageBlockInline(GenericTabularInline):
    model = PageBlock
    extra = 0
    fields = ("kind", "sort_order", "is_visible", "heading", "css_anchor")
    classes = ["collapse"]


_TEXTAREA_STYLE = (
    "width:100%;max-width:100%;min-height:7rem;font-size:1rem;line-height:1.5;"
    "color:#0f172a;background:#ffffff;-webkit-text-fill-color:#0f172a;"
    "border:1px solid #94a3b8;border-radius:0.4rem;padding:0.75rem 0.85rem;"
)


class PageSectionUAForm(forms.ModelForm):
    class Meta:
        model = PageSection
        fields = ("text_ua", "is_active")
        labels = {
            "text_ua": "Текст",
            "is_active": "Показувати на сайті",
        }
        widgets = {
            "text_ua": forms.Textarea(attrs={"rows": 6, "style": _TEXTAREA_STYLE}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Підпис уже в заголовку картки — не дублюємо блідий label Unfold
        self.fields["text_ua"].label = ""


class PageSectionRUForm(forms.ModelForm):
    class Meta:
        model = PageSection
        fields = ("text_ru", "is_active")
        labels = {
            "text_ru": "Текст",
            "is_active": "Показывать на сайте",
        }
        widgets = {
            "text_ru": forms.Textarea(attrs={"rows": 6, "style": _TEXTAREA_STYLE}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["text_ru"].label = ""


class PageSectionInlineBase(UnfoldGenericStackedInline):
    model = PageSection
    extra = 0
    max_num = 400
    can_delete = False
    show_change_link = False
    verbose_name = "Текст"
    verbose_name_plural = "Тексти сторінки — блоки як на сайті"
    ordering = ("block_title", "sort_order", "id")
    template = "admin/cms/edit_inline/stacked_blocks.html"
    classes = ()

    class Media:
        css = {"all": ("admin/css/page_blocks.css",)}

    def has_add_permission(self, request, obj=None):
        return False

    def get_formset(self, request, obj=None, **kwargs):
        FormSet = super().get_formset(request, obj, **kwargs)
        return _make_anchored_formset(FormSet, ("block_title", "sort_order", "id"))


class PageSectionInlineUA(PageSectionInlineBase):
    form = PageSectionUAForm
    fields = ("text_ua", "is_active")


class PageSectionInlineRU(PageSectionInlineBase):
    form = PageSectionRUForm
    fields = ("text_ru", "is_active")


PageSectionInline = PageSectionInlineUA


class SiteImageUAForm(forms.ModelForm):
    class Meta:
        model = SiteImage
        fields = ("label", "image", "image_mobile", "image_alt_ua", "is_active")
        labels = {
            "label": "Назва зображення",
            "image": "Фото (десктоп)",
            "image_mobile": "Фото (мобільне)",
            "image_alt_ua": "Опис фото (alt)",
            "is_active": "Показувати на сайті",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        key = self.instance.image_key if getattr(self.instance, "pk", None) else ""
        apply_site_image_hints(self, image_key=key)


class SiteImageRUForm(forms.ModelForm):
    class Meta:
        model = SiteImage
        fields = ("label", "image", "image_mobile", "image_alt_ru", "is_active")
        labels = {
            "label": "Название изображения",
            "image": "Фото (десктоп)",
            "image_mobile": "Фото (мобильное)",
            "image_alt_ru": "Описание фото (alt)",
            "is_active": "Показывать на сайте",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        key = self.instance.image_key if getattr(self.instance, "pk", None) else ""
        apply_site_image_hints(self, image_key=key)


class SiteImageInlineBase(UnfoldGenericStackedInline):
    model = SiteImage
    extra = 0
    can_delete = False
    show_change_link = False
    verbose_name = "Зображення"
    verbose_name_plural = "Зображення сторінки"
    ordering = ("sort_order", "image_key")
    readonly_fields = ("image_preview",)

    class Media:
        css = {"all": ("admin/css/page_blocks.css",)}

    def has_add_permission(self, request, obj=None):
        return False

    def get_formset(self, request, obj=None, **kwargs):
        FormSet = super().get_formset(request, obj, **kwargs)
        return _make_anchored_formset(FormSet, ("sort_order", "image_key"))

    @admin.display(description="Поточне фото")
    def image_preview(self, obj: SiteImage) -> str:
        if not obj or not obj.pk:
            return "—"
        if obj.image:
            return format_html(
                '<img src="{}" alt="" style="max-height:140px;border-radius:8px;" />',
                obj.image.url,
            )
        if obj.fallback_static:
            return format_html("<code>{}</code>", obj.fallback_static)
        return "—"


class SiteImageInlineUA(SiteImageInlineBase):
    form = SiteImageUAForm
    fields = ("label", "image_preview", "image", "image_mobile", "image_alt_ua", "is_active")


class SiteImageInlineRU(SiteImageInlineBase):
    form = SiteImageRUForm
    fields = ("label", "image_preview", "image", "image_mobile", "image_alt_ru", "is_active")


SiteImageInline = SiteImageInlineUA


def page_content_inlines_for_language(language: str) -> list[type[GenericInlineModelAdmin]]:
    if language == Language.RU:
        return [PageSectionInlineRU, SiteImageInlineRU]
    return [PageSectionInlineUA, SiteImageInlineUA]
