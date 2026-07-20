from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import RequestFactory, TestCase

from src.cms.admin_inlines import PageSectionInlineRU, PageSectionInlineUA
from src.cms.models import PageSection
from src.i18n.models import Language
from src.pages.admin import StaticPageAdmin
from src.pages.models import StaticPage


class StaticPageAdminHubTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.site = AdminSite()
        self.admin = StaticPageAdmin(StaticPage, self.site)
        user_model = get_user_model()
        self.user = user_model.objects.create_superuser(
            "admin", "admin@example.com", "pass"
        )
        self.ua = StaticPage.objects.create(
            slug="tehnichnyj-pasport-na-kvartyru",
            title="Паспорт на квартиру",
            language=Language.UA,
            is_published=True,
            use_block_builder=False,
        )
        self.ru = StaticPage.objects.create(
            slug="tehnichnyj-pasport-na-kvartyru",
            title="Паспорт на квартиру RU",
            language=Language.RU,
            is_published=True,
            use_block_builder=False,
        )
        ct = ContentType.objects.get_for_model(StaticPage)
        self.section = PageSection.objects.create(
            page_slug="tehnichnyj-pasport-na-kvartyru",
            section_key="faq-1",
            label="FAQ 1",
            text_ua="Питання UA",
            text_ru="Вопрос RU",
            content_type=ct,
            object_id=self.ua.pk,
        )

    def test_inlines_language_specific(self):
        request = self.factory.get("/")
        request.user = self.user
        ua_inlines = self.admin.get_inlines(request, self.ua)
        ru_inlines = self.admin.get_inlines(request, self.ru)
        self.assertIn(PageSectionInlineUA, ua_inlines)
        self.assertNotIn(PageSectionInlineRU, ua_inlines)
        self.assertIn(PageSectionInlineRU, ru_inlines)
        self.assertNotIn(PageSectionInlineUA, ru_inlines)

    def test_ru_formset_shows_anchor_sections(self):
        inline = PageSectionInlineRU(StaticPage, self.site)
        request = self.factory.get("/")
        request.user = self.user
        FormSet = inline.get_formset(request, self.ru)
        formset = FormSet(instance=self.ru)
        pks = list(formset.get_queryset().values_list("pk", flat=True))
        self.assertEqual(pks, [self.section.pk])

    def test_ru_save_new_keeps_anchor_link(self):
        inline = PageSectionInlineRU(StaticPage, self.site)
        request = self.factory.get("/")
        request.user = self.user
        FormSet = inline.get_formset(request, self.ru)
        prefix = FormSet.get_default_prefix()
        payload = {
            f"{prefix}-TOTAL_FORMS": "1",
            f"{prefix}-INITIAL_FORMS": "0",
            f"{prefix}-MIN_NUM_FORMS": "0",
            f"{prefix}-MAX_NUM_FORMS": "1000",
            f"{prefix}-0-label": "Новий FAQ",
            f"{prefix}-0-section_key": "faq-new",
            f"{prefix}-0-text_ru": "Новый текст",
            f"{prefix}-0-body_ru": "",
            f"{prefix}-0-is_active": "on",
        }
        formset = FormSet(payload, instance=self.ru)
        self.assertTrue(formset.is_valid(), formset.errors)
        formset.save()
        created = PageSection.objects.get(label="Новий FAQ")
        self.assertEqual(created.object_id, self.ua.pk)
        self.assertEqual(created.page_slug, "tehnichnyj-pasport-na-kvartyru")
        self.assertEqual(created.text_ru, "Новый текст")
