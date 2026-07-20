from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.test import TestCase

from src.cms.models import PageSection
from src.cms.services import link_all_page_content
from src.cms.text_keys import (
    context_looks_like_faq,
    make_section_label,
    ua_text_is_faq_question,
)
from src.i18n.models import Language
from src.pages.models import StaticPage


class TextKeysFaqTests(TestCase):
    def test_faq_label_prefix(self):
        self.assertEqual(
            make_section_label("Скільки коштує?", is_faq=True),
            "FAQ: Скільки коштує?",
        )
        self.assertTrue(ua_text_is_faq_question("Питання?"))

    def test_context_detects_faq_block(self):
        html = '''
        <section class="faq">
          <div class="custom-acc">
            {% t 'Питання?' 'Вопрос?' %}
          </div>
        </section>
        '''
        pos = html.index("{% t")
        self.assertTrue(context_looks_like_faq(html, pos))


class LinkAllPageContentTests(TestCase):
    def test_links_orphan_sections(self):
        page = StaticPage.objects.create(
            slug="tehnichnyj-pasport-na-kvartyru",
            title="Паспорт",
            language=Language.UA,
            is_published=True,
        )
        section = PageSection.objects.create(
            page_slug="tehnichnyj-pasport-na-kvartyru",
            section_key="faq-test",
            label="FAQ test",
            text_ua="Питання?",
        )
        self.assertIsNone(section.content_type_id)
        result = link_all_page_content()
        section.refresh_from_db()
        self.assertEqual(section.object_id, page.pk)
        self.assertGreaterEqual(result["sections"], 1)


class SyncTemplateTextsCommandTests(TestCase):
    def test_sync_imports_passport_faq(self):
        StaticPage.objects.create(
            slug="tehnichnyj-pasport-na-kvartyru",
            title="Паспорт на квартиру",
            language=Language.UA,
            is_published=True,
        )
        call_command("sync_template_texts")
        faqs = PageSection.objects.filter(
            page_slug="tehnichnyj-pasport-na-kvartyru",
            label__startswith="FAQ:",
        )
        self.assertGreaterEqual(faqs.count(), 3)
        ct = ContentType.objects.get_for_model(StaticPage)
        linked = faqs.filter(content_type=ct).count()
        self.assertEqual(linked, faqs.count())
