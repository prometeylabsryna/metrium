"""Інлайни для хабу редагування сторінки (StaticPage)."""

from __future__ import annotations

from django import forms
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericInlineModelAdmin, GenericStackedInline, GenericTabularInline
from django.contrib.contenttypes.models import ContentType
from django.forms.models import BaseModelFormSet
from django.utils.html import format_html

from src.cms.models import PageBlock, PageSection, SiteImage
from src.cms.services import ensure_static_page_links, resolve_page_anchor
from src.i18n.models import Language

try:
    from unfold.overrides import FORMFIELD_OVERRIDES_INLINE
except ImportError:
    FORMFIELD_OVERRIDES_INLINE = {}


class UnfoldGenericStackedInline(GenericStackedInline):
    """Stacked inline — зручні повноширинні поля для редакторів."""

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


class PageSectionUAForm(forms.ModelForm):
    class Meta:
        model = PageSection
        fields = ("label", "text_ua", "body_ua", "is_active")
        labels = {
            "label": "Що це за блок",
            "text_ua": "Текст (українською)",
            "body_ua": "Довгий текст / HTML (якщо є)",
            "is_active": "Показувати на сайті",
        }
        help_texts = {
            "text_ua": "Основний текст, який видно на сторінці. Змініть і збережіть.",
            "body_ua": "Заповнюйте лише якщо потрібен HTML (списки, виділення). Інакше залиште порожнім.",
            "label": "Підказка для вас в адмінці — на сайт не виводиться.",
        }
        widgets = {
            "label": forms.TextInput(attrs={"class": "vTextField", "style": "max-width:48rem;width:100%;"}),
            "text_ua": forms.Textarea(
                attrs={"rows": 5, "cols": 80, "style": "max-width:48rem;width:100%;font-size:1rem;"}
            ),
            "body_ua": forms.Textarea(
                attrs={"rows": 4, "cols": 80, "style": "max-width:48rem;width:100%;"}
            ),
        }


class PageSectionRUForm(forms.ModelForm):
    class Meta:
        model = PageSection
        fields = ("label", "text_ru", "body_ru", "is_active")
        labels = {
            "label": "Что это за блок",
            "text_ru": "Текст (русским)",
            "body_ru": "Длинный текст / HTML (если есть)",
            "is_active": "Показывать на сайте",
        }
        help_texts = {
            "text_ru": "Основной текст на странице. Измените и сохраните.",
            "body_ru": "Только если нужен HTML. Иначе оставьте пустым.",
            "label": "Подсказка в админке — на сайт не выводится.",
        }
        widgets = {
            "label": forms.TextInput(attrs={"class": "vTextField", "style": "max-width:48rem;width:100%;"}),
            "text_ru": forms.Textarea(
                attrs={"rows": 5, "cols": 80, "style": "max-width:48rem;width:100%;font-size:1rem;"}
            ),
            "body_ru": forms.Textarea(
                attrs={"rows": 4, "cols": 80, "style": "max-width:48rem;width:100%;"}
            ),
        }


class PageSectionInlineBase(UnfoldGenericStackedInline):
    """Тексти сторінки — зручні картки з нормальними полями."""

    model = PageSection
    extra = 0
    max_num = 300
    can_delete = False
    show_change_link = False
    verbose_name = "Текстовий блок"
    verbose_name_plural = "Тексти сторінки"
    ordering = ("sort_order", "section_key")
    template = "admin/edit_inline/stacked.html"

    def has_add_permission(self, request, obj=None):
        # Нові блоки зʼявляються через sync_template_texts — редактор лише змінює тексти
        return False

    def get_formset(self, request, obj=None, **kwargs):
        FormSet = super().get_formset(request, obj, **kwargs)
        return _make_anchored_formset(FormSet, ("sort_order", "section_key"))


class PageSectionInlineUA(PageSectionInlineBase):
    form = PageSectionUAForm
    fields = ("label", "text_ua", "body_ua", "is_active")
    verbose_name_plural = "Тексти сторінки (українською) — змінюйте поле «Текст»"


class PageSectionInlineRU(PageSectionInlineBase):
    form = PageSectionRUForm
    fields = ("label", "text_ru", "body_ru", "is_active")
    verbose_name_plural = "Тексты страницы (на русском) — меняйте поле «Текст»"


PageSectionInline = PageSectionInlineUA


class SiteImageUAForm(forms.ModelForm):
    class Meta:
        model = SiteImage
        fields = ("label", "image", "image_mobile", "image_alt_ua", "is_active")
        labels = {
            "label": "Назва зображення",
            "image": "Фото (десктоп)",
            "image_mobile": "Фото (мобільне)",
            "image_alt_ua": "Опис фото (alt, українською)",
            "is_active": "Показувати на сайті",
        }
        help_texts = {
            "image": "Завантажте новий файл — він замінить поточне фото на сайті.",
            "image_mobile": "Опційно: окреме фото для телефону.",
        }


class SiteImageRUForm(forms.ModelForm):
    class Meta:
        model = SiteImage
        fields = ("label", "image", "image_mobile", "image_alt_ru", "is_active")
        labels = {
            "label": "Название изображения",
            "image": "Фото (десктоп)",
            "image_mobile": "Фото (мобильное)",
            "image_alt_ru": "Описание фото (alt, русским)",
            "is_active": "Показывать на сайте",
        }


class SiteImageInlineBase(UnfoldGenericStackedInline):
    model = SiteImage
    extra = 0
    can_delete = False
    show_change_link = False
    verbose_name = "Зображення"
    verbose_name_plural = "Зображення сторінки"
    ordering = ("sort_order", "image_key")
    readonly_fields = ("image_preview",)

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
    verbose_name_plural = "Зображення сторінки"


class SiteImageInlineRU(SiteImageInlineBase):
    form = SiteImageRUForm
    fields = ("label", "image_preview", "image", "image_mobile", "image_alt_ru", "is_active")
    verbose_name_plural = "Изображения страницы"


SiteImageInline = SiteImageInlineUA


def page_content_inlines_for_language(language: str) -> list[type[GenericInlineModelAdmin]]:
    if language == Language.RU:
        return [PageSectionInlineRU, SiteImageInlineRU]
    return [PageSectionInlineUA, SiteImageInlineUA]
