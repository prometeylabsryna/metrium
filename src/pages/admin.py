from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline
from django.db.models import Q
from django.urls import reverse
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from src.cms.admin_inlines import PageBlockInline, page_content_inlines_for_language
from src.cms.models import PageSection, SiteImage
from src.cms.services import ensure_static_page_links, resolve_page_anchor
from src.i18n.models import Language
from src.pages.models import StaticPage
from src.seo.models import SeoMetadata


class SeoMetadataInline(GenericStackedInline):
    model = SeoMetadata
    extra = 0
    max_num = 1
    fields = (
        "seo_title",
        "seo_description",
        "keywords",
        "canonical_url",
        "robots_noindex",
        "robots_nofollow",
        "og_title",
        "og_description",
        "og_image_url",
    )
    verbose_name = "SEO"
    verbose_name_plural = "SEO цієї мовної версії"


PASSPORT_SLUGS = (
    "tehnichni-pasporty-bti",
    "tehnichnyj-pasport-na-kvartyru",
    "tehnichnyj-pasport-na-budynok",
    "elektronnyj-tehnichnyj-pasport",
    "tehnichnyj-pasport-na-budivlyu",
    "tehnichnyj-pasport-na-garazh",
    "tehnichnyj-pasport-na-nezhytlove-prymischennya",
    "tehnichnyj-pasport-na-bagato-kvartyrnyj-budynok",
)

SERVICE_SLUGS = (
    "dovidky",
    "vvedennya-v-ekspluatatsiyu",
    "legalizatsiya-neruhomosti",
    "tehnichna-inventaryzatsiya",
    "dozvilna-dokumentatsiya",
    "zemelna-dokumentatsiya",
    "vysnovky-bti",
    "kadastrovyj-nomer",
    "vytiah-dzk",
    "bti-cina",
    "poslugy-kyiv",
)


class PageKindFilter(admin.SimpleListFilter):
    title = "Тип сторінки"
    parameter_name = "page_kind"

    def lookups(self, request, model_admin):
        return (
            ("passport", "Технічні паспорти"),
            ("services", "Інші послуги БТІ"),
            ("home", "Головна"),
            ("contacts", "Контакти"),
            ("blog", "Блог"),
            ("region", "Регіональні"),
            ("other", "Інше"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == "passport":
            return queryset.filter(slug__in=PASSPORT_SLUGS)
        if value == "services":
            return queryset.filter(slug__in=SERVICE_SLUGS)
        if value == "home":
            return queryset.filter(Q(is_home=True) | Q(slug__in=("home", "")))
        if value == "contacts":
            return queryset.filter(slug="contacts")
        if value == "blog":
            return queryset.filter(slug__startswith="blog")
        if value == "region":
            return queryset.filter(Q(slug__contains="oblast") | Q(location__gt=""))
        if value == "other":
            known = set(PASSPORT_SLUGS) | set(SERVICE_SLUGS) | {"home", "contacts", ""}
            return queryset.exclude(slug__in=known).exclude(is_home=True).exclude(
                slug__startswith="blog"
            ).exclude(slug__contains="oblast").exclude(location__gt="")
        return queryset


@admin.register(StaticPage)
class StaticPageAdmin(ModelAdmin):
    list_display = (
        "title",
        "slug",
        "language",
        "is_published",
        "translation_link",
        "content_source_hint",
    )
    list_filter = ("language", "is_published", PageKindFilter, "template_key", "use_block_builder")
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("content_edit_hint", "quick_links")
    list_per_page = 50

    fieldsets = (
        (
            "Основне",
            {
                "fields": ("title", "slug", "language", "is_published", "is_home", "quick_links"),
                "classes": ["tab"],
            },
        ),
        (
            "Шаблон",
            {
                "fields": ("template_key", "use_block_builder", "location"),
                "classes": ["tab"],
            },
        ),
        (
            "Контент",
            {
                "fields": ("content_edit_hint", "body_legacy", "published_at"),
                "classes": ["tab"],
            },
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related()

    def _anchor_context(self, obj: StaticPage | None):
        if not obj or not obj.pk:
            return None, False
        ensure_static_page_links(obj)
        anchor = resolve_page_anchor(obj.slug)
        return anchor, bool(anchor and anchor.pk == obj.pk)

    def _sibling(self, obj: StaticPage) -> StaticPage | None:
        if not obj or not obj.pk:
            return None
        return (
            StaticPage.objects.filter(slug=obj.slug)
            .exclude(pk=obj.pk)
            .order_by("language")
            .first()
        )

    @admin.display(description="Переклад")
    def translation_link(self, obj: StaticPage) -> str:
        sibling = self._sibling(obj)
        if not sibling:
            return "—"
        label = "RU" if sibling.language == Language.RU else "UA"
        return format_html(
            '<a href="{}">{} ↗</a>',
            reverse("admin:pages_staticpage_change", args=[sibling.pk]),
            label,
        )

    @admin.display(description="Швидкі посилання")
    def quick_links(self, obj: StaticPage) -> str:
        if not obj or not obj.pk:
            return "Збережіть запис, щоб побачити посилання."

        links: list[str] = []
        public = obj.get_absolute_url()
        links.append(
            f'<a class="button" href="{public}" target="_blank" rel="noopener">'
            f"Відкрити на сайті ↗</a>"
        )

        sibling = self._sibling(obj)
        if sibling:
            lang = "російською" if sibling.language == Language.RU else "українською"
            url = reverse("admin:pages_staticpage_change", args=[sibling.pk])
            links.append(
                f'<a class="button" href="{url}">Редагувати версію {lang} ↗</a>'
            )

        links.append(
            '<a class="button" href="/admin/cms/pagesection/?page_slug__exact=header">'
            "Меню (шапка) ↗</a>"
        )
        links.append(
            '<a class="button" href="/admin/cms/pagesection/?page_slug__exact=footer">'
            "Футер ↗</a>"
        )

        if obj.is_home or obj.slug in ("home", ""):
            links.append(
                '<a class="button" href="/admin/cms/homeservicecard/">'
                "Картки послуг на головній ↗</a>"
            )
            links.append(
                '<a class="button" href="/admin/cms/homewhyitem/">'
                "Переваги на головній ↗</a>"
            )
            links.append(
                '<a class="button" href="/admin/cms/homestatitem/">'
                "Статистика на головній ↗</a>"
            )

        if obj.slug == "blog" or obj.slug.startswith("blog"):
            links.append(
                '<a class="button" href="/admin/blog/blogpost/">Пости блогу ↗</a>'
            )

        return format_html(
            '<p style="display:flex;flex-wrap:wrap;gap:.5rem;margin:0;">{}</p>',
            format_html("".join(links)),
        )

    @admin.display(description="Редагування контенту")
    def content_edit_hint(self, obj: StaticPage) -> str:
        if not obj or not obj.pk:
            return "Збережіть запис, щоб редагувати тексти, FAQ, фото й SEO нижче."

        anchor, _is_anchor = self._anchor_context(obj)
        lang_label = "українською" if obj.language == Language.UA else "російською"
        parts: list[str] = [
            format_html(
                "<ol style='margin:0;padding-left:1.25rem;line-height:1.55;'>"
                "<li>Нижче кожен блок — окремий текст на сайті (заголовок, абзац, FAQ тощо).</li>"
                "<li>Змінюйте поле <strong>«Текст (… )»</strong> — це те, що бачать відвідувачі.</li>"
                "<li>Поле «Що це за блок» — лише підказка для вас, на сайт не йде.</li>"
                "<li>Мова цієї картки: <strong>{}</strong>. Іншу мову відкрийте кнопкою вище.</li>"
                "</ol>",
                lang_label,
            )
        ]

        if anchor:
            sections = PageSection.objects.filter(
                content_type__isnull=False, object_id=anchor.pk
            ).count()
            images = SiteImage.objects.filter(
                content_type__isnull=False, object_id=anchor.pk
            ).count()
            parts.append(
                format_html(
                    "<p style='margin-top:.75rem;'>На цій сторінці: "
                    "<strong>{}</strong> текстових блоків, <strong>{}</strong> зображень.</p>",
                    sections,
                    images,
                )
            )

        if obj.use_block_builder:
            parts.append(
                format_html(
                    "<p>Також є блоки конструктора нижче (legacy).</p>"
                )
            )

        return format_html("".join(str(p) for p in parts))

    @admin.display(description="Де редагувати")
    def content_source_hint(self, obj: StaticPage) -> str:
        anchor, _ = self._anchor_context(obj)
        if anchor and (
            PageSection.objects.filter(content_type__isnull=False, object_id=anchor.pk).exists()
            or SiteImage.objects.filter(content_type__isnull=False, object_id=anchor.pk).exists()
        ):
            return "Тексти / FAQ / фото / SEO — на цій картці"
        if obj.use_block_builder:
            return "Блоки + SEO на цій картці"
        return "Body legacy / SEO"

    def get_inlines(self, request, obj=None):
        inlines: list = []
        if obj and obj.pk:
            inlines.extend(page_content_inlines_for_language(obj.language))
            inlines.append(SeoMetadataInline)
        if obj is None or obj.use_block_builder:
            inlines.append(PageBlockInline)
        return inlines

    def save_formset(self, request, form, formset, change):
        if formset.model in (PageSection, SiteImage):
            instances = formset.save(commit=False)
            anchor = resolve_page_anchor(form.instance.slug) or form.instance
            for instance in instances:
                if not instance.page_slug:
                    instance.page_slug = (
                        "home" if form.instance.is_home else form.instance.slug
                    )
                instance.save()
            formset.save_m2m()
            for obj in formset.deleted_objects:
                obj.delete()
            # Переконуємось, що GFK лишається на якорі після збереження з RU-картки
            ensure_static_page_links(anchor)
        else:
            formset.save()
