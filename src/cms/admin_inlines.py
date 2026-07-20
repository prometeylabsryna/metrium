"""Інлайни для хабу редагування сторінки (StaticPage)."""

from __future__ import annotations

from django.contrib import admin
from django.contrib.contenttypes.admin import GenericInlineModelAdmin, GenericTabularInline
from django.contrib.contenttypes.models import ContentType
from django.forms.models import BaseModelFormSet
from django.utils.html import format_html

from src.cms.models import PageBlock, PageSection, SiteImage
from src.cms.page_labels import page_public_url
from src.cms.services import ensure_static_page_links, resolve_page_anchor
from src.i18n.models import Language

try:
    from unfold.mixins import BaseModelAdminMixin
except ImportError:  # серверна збірка unfold без цього mixin
    BaseModelAdminMixin = object  # type: ignore[misc,assignment]

try:
    from unfold.overrides import FORMFIELD_OVERRIDES_INLINE
except ImportError:
    FORMFIELD_OVERRIDES_INLINE = {}


class UnfoldGenericTabularInline(BaseModelAdminMixin, GenericTabularInline):
    """Generic tabular inline; стилі Unfold — якщо mixin доступний у встановленій версії."""

    formfield_overrides = FORMFIELD_OVERRIDES_INLINE
    readonly_preprocess_fields: dict = {}


class _AnchoredGenericFormSetMixin:
    """Показує/зберігає контент на якірній StaticPage (спільний для UA і RU)."""

    def get_queryset(self):
        instance = self.instance
        if not instance or not instance.pk:
            return self.model.objects.none()

        ensure_static_page_links(instance)
        anchor = resolve_page_anchor(instance.slug)
        if not anchor:
            return self.model.objects.none()

        ct = ContentType.objects.get_for_model(instance.__class__)
        return self.model.objects.filter(content_type=ct, object_id=anchor.pk).order_by(
            *self._order_by
        )

    def save_new(self, form, commit=True):
        """Привʼязуємо до якоря; не викликаємо BaseGenericInlineFormSet.save_new
        (воно перезапише object_id на поточну мовну картку)."""
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


class PageSectionInlineBase(UnfoldGenericTabularInline):
    """Тексти сторінки — спільні записи, поля залежать від мови картки."""

    model = PageSection
    extra = 0
    readonly_fields = ("site_preview_link",)
    show_change_link = True
    verbose_name = "Текст / FAQ"
    verbose_name_plural = "Тексти та FAQ"
    ordering = ("sort_order", "section_key")

    def get_formset(self, request, obj=None, **kwargs):
        FormSet = super().get_formset(request, obj, **kwargs)
        return _make_anchored_formset(FormSet, ("sort_order", "section_key"))

    @admin.display(description="")
    def site_preview_link(self, obj: PageSection) -> str:
        if not obj or not obj.pk:
            return "—"
        return format_html(
            '<a class="button" href="{}" target="_blank" rel="noopener">На сайті ↗</a>',
            page_public_url(obj.page_slug),
        )


class PageSectionInlineUA(PageSectionInlineBase):
    fields = ("label", "section_key", "text_ua", "body_ua", "is_active", "site_preview_link")
    verbose_name_plural = "Тексти та FAQ (українською)"


class PageSectionInlineRU(PageSectionInlineBase):
    fields = ("label", "section_key", "text_ru", "body_ru", "is_active", "site_preview_link")
    verbose_name_plural = "Тексти та FAQ (російською)"


# Зворотна сумісність імпортів
PageSectionInline = PageSectionInlineUA


class SiteImageInlineBase(UnfoldGenericTabularInline):
    """Зображення сторінки — спільні файли, alt залежать від мови картки."""

    model = SiteImage
    extra = 0
    show_change_link = True
    verbose_name = "Зображення"
    verbose_name_plural = "Зображення сторінки"
    ordering = ("sort_order", "image_key")

    def get_formset(self, request, obj=None, **kwargs):
        FormSet = super().get_formset(request, obj, **kwargs)
        return _make_anchored_formset(FormSet, ("sort_order", "image_key"))


class SiteImageInlineUA(SiteImageInlineBase):
    fields = ("label", "image_key", "image", "image_mobile", "image_alt_ua", "is_active")
    verbose_name_plural = "Зображення (alt українською)"


class SiteImageInlineRU(SiteImageInlineBase):
    fields = ("label", "image_key", "image", "image_mobile", "image_alt_ru", "is_active")
    verbose_name_plural = "Зображення (alt російською)"


SiteImageInline = SiteImageInlineUA


def page_content_inlines_for_language(language: str) -> list[type[GenericInlineModelAdmin]]:
    if language == Language.RU:
        return [PageSectionInlineRU, SiteImageInlineRU]
    return [PageSectionInlineUA, SiteImageInlineUA]
