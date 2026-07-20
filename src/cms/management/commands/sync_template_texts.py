from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from src.cms.models import PageSection
from src.cms.services import clear_section_cache, link_all_page_content
from src.cms.template_blocks import extract_template_text_items
from src.cms.text_keys import (
    BI_TAG_RE,
    SECTION_BODY_TAG_RE,
    SECTION_TAG_RE,
    make_label,
    page_slug_from_template_path,
)

MANUAL_SECTIONS: list[dict] = [
    # Header navigation
    {"page_slug": "header", "section_key": "nav.home", "label": "Меню: Головна", "text_ua": "Головна", "text_ru": "Главная"},
    {"page_slug": "header", "section_key": "nav.services", "label": "Меню: Послуги БТІ", "text_ua": "Послуги БТІ", "text_ru": "Услуги БТИ"},
    {"page_slug": "header", "section_key": "nav.passport", "label": "Меню: Технічний паспорт", "text_ua": "Технічний паспорт БТІ", "text_ru": "Технический паспорт БТИ"},
    {"page_slug": "header", "section_key": "nav.passport.kvartyra", "label": "Меню: На квартиру", "text_ua": "На квартиру", "text_ru": "На квартиру"},
    {"page_slug": "header", "section_key": "nav.passport.budynok", "label": "Меню: На будинок", "text_ua": "На будинок", "text_ru": "На дом"},
    {"page_slug": "header", "section_key": "nav.passport.elektronnyj", "label": "Меню: Електронний", "text_ua": "Електронний", "text_ru": "Электронный"},
    {"page_slug": "header", "section_key": "nav.passport.budivlya", "label": "Меню: На будівлю", "text_ua": "На будівлю", "text_ru": "На здание"},
    {"page_slug": "header", "section_key": "nav.passport.garazh", "label": "Меню: На гараж", "text_ua": "На гараж", "text_ru": "На гараж"},
    {"page_slug": "header", "section_key": "nav.passport.nezhytlove", "label": "Меню: Нежитлове", "text_ua": "На нежитлове приміщення", "text_ru": "На нежилое помещение"},
    {"page_slug": "header", "section_key": "nav.passport.mbd", "label": "Меню: Багатоквартирний", "text_ua": "На багатоквартирний будинок", "text_ru": "На многоквартирный дом"},
    {"page_slug": "header", "section_key": "nav.dovidky", "label": "Меню: Довідки", "text_ua": "Довідки БТІ", "text_ru": "Справки БТИ"},
    {"page_slug": "header", "section_key": "nav.vvedennya", "label": "Меню: Введення", "text_ua": "Введення в експлуатацію", "text_ru": "Введение в эксплуатацию"},
    {"page_slug": "header", "section_key": "nav.legalizatsiya", "label": "Меню: Легалізація", "text_ua": "Легалізація нерухомості", "text_ru": "Легализация недвижимости"},
    {"page_slug": "header", "section_key": "nav.inventaryzatsiya", "label": "Меню: Інвентаризація", "text_ua": "Технічна інвентаризація", "text_ru": "Техническая инвентаризация"},
    {"page_slug": "header", "section_key": "nav.dozvilna", "label": "Меню: Дозвільна", "text_ua": "Дозвільна документація", "text_ru": "Разрешительная документация"},
    {"page_slug": "header", "section_key": "nav.zemelna", "label": "Меню: Земельна", "text_ua": "Земельна документація", "text_ru": "Земельная документация"},
    {"page_slug": "header", "section_key": "nav.vysnovky", "label": "Меню: Висновки", "text_ua": "Висновки БТІ", "text_ru": "Заключения БТИ"},
    {"page_slug": "header", "section_key": "nav.kadastr", "label": "Меню: Кадастр", "text_ua": "Кадастровий номер", "text_ru": "Кадастровый номер"},
    {"page_slug": "header", "section_key": "nav.dzk", "label": "Меню: ДЗК", "text_ua": "Витяг ДЗК", "text_ru": "Выписка ГЗК"},
    {"page_slug": "header", "section_key": "nav.blog", "label": "Меню: Блог", "text_ua": "Блог", "text_ru": "Блог"},
    {"page_slug": "header", "section_key": "nav.contacts", "label": "Меню: Контакти", "text_ua": "Контакти", "text_ru": "Контакты"},
    {"page_slug": "header", "section_key": "ui.open_menu", "label": "UI: Відкрити меню", "text_ua": "Відкрити меню", "text_ru": "Открыть меню"},
    {"page_slug": "header", "section_key": "ui.close_menu", "label": "UI: Закрити меню", "text_ua": "Закрити меню", "text_ru": "Закрыть меню"},
    {"page_slug": "header", "section_key": "ui.mobile_nav", "label": "UI: Мобільне меню", "text_ua": "Мобільне меню", "text_ru": "Мобильное меню"},
    {"page_slug": "header", "section_key": "ui.main_nav", "label": "UI: Головне меню", "text_ua": "Головне меню", "text_ru": "Главное меню"},
    # Footer
    {"page_slug": "footer", "section_key": "title.clients", "label": "Футер: Клієнтам", "text_ua": "Клієнтам", "text_ru": "Клиентам"},
    {"page_slug": "footer", "section_key": "title.schedule", "label": "Футер: Графік", "text_ua": "Графік роботи", "text_ru": "График работы"},
    {"page_slug": "footer", "section_key": "title.contacts", "label": "Футер: Контакти", "text_ua": "Контактні дані", "text_ru": "Контактные данные"},
    {"page_slug": "footer", "section_key": "label.messengers", "label": "Футер: Месенджери", "text_ua": "Месенджери", "text_ru": "Мессенджеры"},
    {"page_slug": "footer", "section_key": "label.socials", "label": "Футер: Соцмережі", "text_ua": "Соціальні мережі", "text_ru": "Социальные сети"},
    {"page_slug": "footer", "section_key": "nav.info", "label": "Футер: Інфо", "text_ua": "Інфо", "text_ru": "Инфо"},
    {"page_slug": "footer", "section_key": "form.phone", "label": "Футер: placeholder телефону", "text_ua": "Ваш телефон", "text_ru": "Ваш телефон"},
    {"page_slug": "footer", "section_key": "form.submit", "label": "Футер: кнопка відправки", "text_ua": "Відправити", "text_ru": "Отправить"},
    # Global UI
    {"page_slug": "global", "section_key": "toast.title", "label": "Toast: заголовок", "text_ua": "Дякуємо за звернення!", "text_ru": "Спасибо за обращение!"},
    {"page_slug": "global", "section_key": "toast.text", "label": "Toast: текст", "text_ua": "Менеджер зв'яжеться з вами протягом 5 хвилин", "text_ru": "Менеджер свяжется с вами в течение 5 минут"},
    {"page_slug": "global", "section_key": "toast.close", "label": "Toast: закрити", "text_ua": "Закрити", "text_ru": "Закрыть"},
    {"page_slug": "global", "section_key": "floating.call", "label": "Плаваюча кнопка: дзвінок", "text_ua": "Зателефонувати", "text_ru": "Позвонить"},
    {"page_slug": "global", "section_key": "foto.marquee", "label": "Фото: заголовок", "text_ua": "Фото наших робіт", "text_ru": "Фото наших работ"},
    # About page
    {"page_slug": "about", "section_key": "breadcrumb.home", "label": "About: breadcrumb home", "text_ua": "Головна", "text_ru": "Главная"},
    {"page_slug": "about", "section_key": "ui.breadcrumb", "label": "About: навігація", "text_ua": "Навігація", "text_ru": "Навигация"},
    {"page_slug": "about", "section_key": "why.image_alt", "label": "About: alt фото", "text_ua": "Про Метріум", "text_ru": "О Метриум"},
    {"page_slug": "about", "section_key": "qual.garant_alt", "label": "About: alt гарантія", "text_ua": "Гарантія якості", "text_ru": "Гарантия качества"},
    {"page_slug": "about", "section_key": "breadcrumb.current", "label": "About: breadcrumb", "text_ua": "Про нас", "text_ru": "О нас"},
    {"page_slug": "about", "section_key": "hero.title", "label": "About: H1", "text_ua": "Про нас", "text_ru": "О нас"},
    {"page_slug": "about", "section_key": "hero.subtitle", "label": "About: підзаголовок", "text_ua": "Офіційна компанія з виготовлення технічних паспортів БТІ у Київській області", "text_ru": "Официальная компания по изготовлению технических паспортов БТИ в Киевской области"},
    {"page_slug": "about", "section_key": "why.label", "label": "About: секція 1 label", "text_ua": "Офіційні дані", "text_ru": "Официальные данные"},
    {"page_slug": "about", "section_key": "why.title", "label": "About: Хто ми", "text_ua": "Хто ми?", "text_ru": "Кто мы?"},
    {"page_slug": "about", "section_key": "why.item1.title", "label": "About: item1 title", "text_ua": "Організаційно-правова норма", "text_ru": "Организационно-правовая норма"},
    {"page_slug": "about", "section_key": "why.item1.text", "label": "About: item1 text", "text_ua": "Приватне підприємство «Метріум» — ліцензована компанія, що надає послуги у сфері технічної інвентаризації об'єктів нерухомості на підставі закону України.", "text_ru": "Частное предприятие «Метриум» — лицензированная компания, предоставляющая услуги в сфере технической инвентаризации объектов недвижимости на основании закона Украины."},
    {"page_slug": "about", "section_key": "why.item2.title", "label": "About: item2 title", "text_ua": "Керівник", "text_ru": "Руководитель"},
    {"page_slug": "about", "section_key": "why.item2.text", "label": "About: item2 text", "text_ua": "Кравченко Олег Миколайович — сертифікований технічний інвентаризатор з досвідом 12+ років", "text_ru": "Кравченко Олег Николаевич — сертифицированный технический инвентаризатор с опытом 12+ лет"},
    {"page_slug": "about", "section_key": "why.item3.title", "label": "About: item3 title", "text_ua": "Код ЄДРПОУ", "text_ru": "Код ЕГРПОУ"},
    {"page_slug": "about", "section_key": "why.item3.text", "label": "About: item3 text", "text_ua": "44ХХХХХХ (уточнюється у договорі)", "text_ru": "44ХХХХХХ (уточняется в договоре)"},
    {"page_slug": "about", "section_key": "why.item4.title", "label": "About: item4 title", "text_ua": "Адреса", "text_ru": "Адрес"},
    {"page_slug": "about", "section_key": "why.item4.text", "label": "About: item4 text", "text_ua": "вул. Стельмаха 9а, м. Ірпінь, Київська обл., 08200", "text_ru": "ул. Стельмаха 9а, г. Ирпень, Киевская обл., 08200"},
    {"page_slug": "about", "section_key": "qual.label", "label": "About: qual label", "text_ua": "Кваліфікація", "text_ru": "Квалификация"},
    {"page_slug": "about", "section_key": "qual.title", "label": "About: qual title", "text_ua": "Наша ліцензія та повноваження", "text_ru": "Наша лицензия и полномочия"},
    {"page_slug": "about", "section_key": "qual.text", "label": "About: qual text", "text_ua": "Всі фахівці Метріум мають відповідні кваліфікаційні сертифікати та включені до Державного реєстру технічних інвентаризаторів. Це означає, що технічні паспорти, виготовлені нашою компанією, мають повну юридичну силу та визнаються всіма нотаріусами, банками та державними органами.", "text_ru": "Все специалисты Метриум имеют соответствующие квалификационные сертификаты и включены в Государственный реестр технических инвентаризаторов. Это означает, что технические паспорта, изготовленные нашей компанией, имеют полную юридическую силу и признаются всеми нотариусами, банками и государственными органами."},
    {"page_slug": "about", "section_key": "qual.list", "label": "About: qual list HTML", "body_ua": "<li>Сертифікат технічного інвентаризатора серії ТІ №ХXXXXX</li><li>Внесення до Державного реєстру суб'єктів технічної інвентаризації</li><li>Право на проведення технічної інвентаризації по всій Київській та Житомирській областях</li><li>Членство в Асоціації фахівців у сфері нерухомості України</li>", "body_ru": "<li>Сертификат технического инвентаризатора серии ТИ №ХXXXXX</li><li>Внесение в Государственный реестр субъектов технической инвентаризации</li><li>Право на проведение технической инвентаризации по всей Киевской и Житомирской областям</li><li>Членство в Ассоциации специалистов в сфере недвижимости Украины</li>"},
    {"page_slug": "about", "section_key": "dark.accent", "label": "About: accent title", "text_ua": "Чому обирають нас?", "text_ru": "Почему выбирают нас?"},
    {"page_slug": "about", "section_key": "dark.bullet1", "label": "About: bullet 1", "body_ua": "<strong>12</strong><br>років досвіду в технічній інвентаризації", "body_ru": "<strong>12</strong><br>лет опыта в технической инвентаризации"},
    {"page_slug": "about", "section_key": "dark.bullet2", "label": "About: bullet 2", "body_ua": "<strong>10</strong><br>філій по Києву та Київській області", "body_ru": "<strong>10</strong><br>филиалов по Киеву и Киевской области"},
    {"page_slug": "about", "section_key": "dark.bullet3", "label": "About: bullet 3", "body_ua": "<strong>5 000+</strong><br>успішних проєктів", "body_ru": "<strong>5 000+</strong><br>успешных проектов"},
    {"page_slug": "about", "section_key": "dark.bullet4", "label": "About: bullet 4", "body_ua": "<strong>20+</strong><br>об'єктів на тиждень", "body_ru": "<strong>20+</strong><br>объектов в неделю"},
    {"page_slug": "about", "section_key": "dark.text1", "label": "About: dark p1", "text_ua": "Метріум — це команда сертифікованих фахівців, яка щодня допомагає власникам нерухомості в Київській області легально оформити свої об'єкти.", "text_ru": "Метриум — это команда сертифицированных специалистов, которая ежедневно помогает владельцам недвижимости в Киевской области легально оформить свои объекты."},
    {"page_slug": "about", "section_key": "dark.text2", "label": "About: dark p2", "text_ua": "Ми не просто видаємо документи — ми пояснюємо кожен крок, консультуємо безкоштовно та залишаємось поруч навіть після завершення роботи.", "text_ru": "Мы не просто выдаем документы — мы объясняем каждый шаг, консультируем бесплатно и остаемся рядом даже после завершения работы."},
    {"page_slug": "about", "section_key": "dark.text3", "label": "About: dark p3", "body_ua": "<strong>Технічний паспорт БТІ</strong> — це інформаційний документ, в якому наведено всі технічні характеристики об'єкта нерухомості. Він необхідний при купівлі-продажу, спадкуванні та будь-яких нотаріальних угодах.", "body_ru": "<strong>Технический паспорт БТИ</strong> — это информационный документ, в котором приведены все технические характеристики объекта недвижимости. Он необходим при купле-продаже, наследовании и любых нотариальных сделках."},
    {"page_slug": "about", "section_key": "dark.cta", "label": "About: CTA", "text_ua": "Замовити консультацію", "text_ru": "Заказать консультацию"},
    {"page_slug": "about", "section_key": "suggest.title", "label": "About: suggest title", "text_ua": "Що входить у послугу?", "text_ru": "Что входит в услугу?"},
    {"page_slug": "about", "section_key": "suggest.item1", "label": "About: suggest 1", "text_ua": "Виїзд техніка на об'єкт та обмірювання", "text_ru": "Выезд техника на объект и обмер"},
    {"page_slug": "about", "section_key": "suggest.item2", "label": "About: suggest 2", "text_ua": "Фотофіксація та складання плану", "text_ru": "Фотофиксация и составление плана"},
    {"page_slug": "about", "section_key": "suggest.item3", "label": "About: suggest 3", "text_ua": "Занесення даних до Реєстру", "text_ru": "Внесение данных в Реестр"},
    {"page_slug": "about", "section_key": "suggest.item4", "label": "About: suggest 4", "text_ua": "Видача паперового та електронного екземплярів", "text_ru": "Выдача бумажного и электронного экземпляров"},
    {"page_slug": "about", "section_key": "suggest.item5", "label": "About: suggest 5", "text_ua": "Консультація щодо подальших дій", "text_ru": "Консультация по дальнейшим действиям"},
    {"page_slug": "about", "section_key": "suggest.item6", "label": "About: suggest 6", "text_ua": "Безкоштовна доставка в межах Ірпеня", "text_ru": "Бесплатная доставка в пределах Ирпеня"},
    # Home page sections
    {"page_slug": "home", "section_key": "services.label", "label": "Головна: мітка послуг", "text_ua": "Наші послуги", "text_ru": "Наши услуги"},
    {"page_slug": "home", "section_key": "services.title", "label": "Головна: заголовок послуг", "text_ua": "Послуги", "text_ru": "Услуги"},
    {"page_slug": "home", "section_key": "calc.label", "label": "Головна: мітка калькулятора", "text_ua": "Онлайн-калькулятор", "text_ru": "Онлайн-калькулятор"},
    {"page_slug": "home", "section_key": "calc.title", "label": "Головна: заголовок калькулятора", "text_ua": "Вартість техпаспорта БТІ", "text_ru": "Стоимость техпаспорта БТИ"},
    {"page_slug": "home", "section_key": "why.title", "label": "Головна: чому ми", "text_ua": "Чому варто обрати наше БТІ?", "text_ru": "Почему стоит выбрать наше БТИ?"},
    {"page_slug": "home", "section_key": "about.accent", "label": "Головна: акцент про нас", "text_ua": "ПРИВАТНЕ БТІ METRIUM", "text_ru": "ЧАСТНОЕ БТИ METRIUM"},
]


class Command(BaseCommand):
    help = "Імпортує тексти з шаблонів у PageSection для редагування в адмінці"

    def add_arguments(self, parser):
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Перезаписати існуючі секції текстами з шаблонів",
        )
        parser.add_argument(
            "--fill-empty",
            action="store_true",
            default=True,
            help="Заповнити порожні поля текстами з шаблонів (за замовчуванням увімкнено)",
        )
        parser.add_argument(
            "--no-fill-empty",
            action="store_false",
            dest="fill_empty",
            help="Не заповнювати порожні поля",
        )

    def handle(self, *args, **options):
        overwrite = options["overwrite"]
        fill_empty = options["fill_empty"]
        templates_dir = Path(settings.BASE_DIR) / "templates"
        created = 0
        updated = 0
        filled = 0
        skipped = 0
        sort_counters: dict[str, int] = {}

        seen: set[tuple[str, str]] = set()
        manual_by_key = {
            (item["page_slug"], item["section_key"]): item for item in MANUAL_SECTIONS
        }

        for item in MANUAL_SECTIONS:
            key = (item["page_slug"], item["section_key"])
            if key in seen:
                continue
            seen.add(key)
            slug = item["page_slug"]
            sort_counters[slug] = sort_counters.get(slug, 0) + 10
            block_map = {
                "header": "Меню (шапка сайту)",
                "footer": "Футер",
                "global": "Спільні тексти (форми, toast)",
                "home": "Головна",
                "about": "Про нас",
            }
            action = self._upsert_section(
                {
                    **item,
                    "sort_order": sort_counters[slug],
                    "block_title": item.get("block_title") or block_map.get(slug, "Тексти"),
                },
                overwrite,
                fill_empty,
            )
            created, updated, filled, skipped = self._tally(
                action, created, updated, filled, skipped
            )

        for path in sorted(templates_dir.rglob("*.html")):
            rel = str(path.relative_to(templates_dir))
            page_slug = page_slug_from_template_path(rel)
            content = path.read_text(encoding="utf-8")

            for item in extract_template_text_items(content):
                key = (page_slug, item.section_key)
                if key in seen:
                    continue
                seen.add(key)
                action = self._upsert_section(
                    {
                        "page_slug": page_slug,
                        "section_key": item.section_key,
                        "label": item.label,
                        "block_title": item.block_title,
                        "text_ua": item.ua,
                        "text_ru": item.ru,
                        "sort_order": item.sort_order,
                        "is_faq": item.is_faq,
                    },
                    overwrite,
                    fill_empty,
                )
                created, updated, filled, skipped = self._tally(
                    action, created, updated, filled, skipped
                )

            for match in BI_TAG_RE.finditer(content):
                slug = match.group(1)
                section_key = match.group(2)
                ua = match.group(3).replace("\\'", "'")
                ru = match.group(4).replace("\\'", "'")
                key = (slug, section_key)
                if key in seen:
                    continue
                seen.add(key)
                manual = manual_by_key.get(key, {})
                sort_counters[slug] = sort_counters.get(slug, 0) + 10
                action = self._upsert_section(
                    {
                        "page_slug": slug,
                        "section_key": section_key,
                        "label": manual.get("label") or make_label(ua),
                        "block_title": manual.get("block_title") or "Тексти сторінки",
                        "text_ua": ua,
                        "text_ru": ru,
                        "body_ua": manual.get("body_ua", ""),
                        "body_ru": manual.get("body_ru", ""),
                        "sort_order": sort_counters[slug],
                    },
                    overwrite,
                    fill_empty,
                )
                created, updated, filled, skipped = self._tally(
                    action, created, updated, filled, skipped
                )

            for match in SECTION_TAG_RE.finditer(content):
                slug = match.group(1)
                section_key = match.group(2)
                ua = match.group(3).replace("\\'", "'")
                ru = match.group(4).replace("\\'", "'")
                key = (slug, section_key)
                if key in seen:
                    continue
                seen.add(key)
                manual = manual_by_key.get(key, {})
                sort_counters[slug] = sort_counters.get(slug, 0) + 10
                action = self._upsert_section(
                    {
                        "page_slug": slug,
                        "section_key": section_key,
                        "label": manual.get("label") or make_label(ua),
                        "block_title": manual.get("block_title") or "Тексти сторінки",
                        "text_ua": ua,
                        "text_ru": ru,
                        "sort_order": sort_counters[slug],
                    },
                    overwrite,
                    fill_empty,
                )
                created, updated, filled, skipped = self._tally(
                    action, created, updated, filled, skipped
                )

            for match in SECTION_BODY_TAG_RE.finditer(content):
                slug = match.group(1)
                section_key = match.group(2)
                key = (slug, section_key)
                if key in seen:
                    continue
                seen.add(key)
                manual = manual_by_key.get(key, {})
                sort_counters[slug] = sort_counters.get(slug, 0) + 10
                action = self._upsert_section(
                    {
                        "page_slug": slug,
                        "section_key": section_key,
                        "label": manual.get("label") or section_key.replace(".", " · "),
                        "block_title": manual.get("block_title") or "Тексти сторінки",
                        "text_ua": manual.get("text_ua", ""),
                        "text_ru": manual.get("text_ru", ""),
                        "body_ua": manual.get("body_ua", ""),
                        "body_ru": manual.get("body_ru", ""),
                        "sort_order": sort_counters[slug],
                    },
                    overwrite,
                    fill_empty,
                )
                created, updated, filled, skipped = self._tally(
                    action, created, updated, filled, skipped
                )

        # Застарілі записи без блоку — в кінець списку, щоб не плутали редактора
        orphans = list(PageSection.objects.filter(block_title="").order_by("id"))
        for index, orphan in enumerate(orphans):
            orphan.block_title = "Інші тексти"
            if orphan.sort_order < 9000:
                orphan.sort_order = 9000 + index
            orphan.save(update_fields=["block_title", "sort_order"])

        clear_section_cache()
        linked = link_all_page_content()
        self.stdout.write(
            self.style.SUCCESS(
                f"Готово: створено {created}, оновлено {updated}, "
                f"заповнено порожніх {filled}, пропущено {skipped}"
            )
        )
        if orphans:
            self.stdout.write(
                self.style.WARNING(
                    f"Без блоку з шаблону: {len(orphans)} → група «Інші тексти»"
                )
            )
        self.stdout.write(
            self.style.SUCCESS(
                f"Привʼязка до сторінок: {linked['pages']} сторінок, "
                f"{linked['sections']} текстів, {linked['images']} зображень"
            )
        )

    @staticmethod
    def _tally(action: str, created: int, updated: int, filled: int, skipped: int) -> tuple[int, int, int, int]:
        if action == "created":
            created += 1
        elif action == "updated":
            updated += 1
        elif action == "filled":
            filled += 1
        else:
            skipped += 1
        return created, updated, filled, skipped

    def _upsert_section(self, data: dict, overwrite: bool, fill_empty: bool) -> str:
        defaults = {
            "label": data["label"],
            "block_title": data.get("block_title", ""),
            "text_ua": data.get("text_ua", ""),
            "text_ru": data.get("text_ru", ""),
            "body_ua": data.get("body_ua", ""),
            "body_ru": data.get("body_ru", ""),
            "sort_order": data.get("sort_order", 0),
            "is_active": True,
        }
        obj, created = PageSection.objects.get_or_create(
            page_slug=data["page_slug"],
            section_key=data["section_key"],
            defaults=defaults,
        )
        if created:
            return "created"
        if overwrite:
            for field, value in defaults.items():
                setattr(obj, field, value)
            obj.save()
            return "updated"
        if fill_empty:
            changed = False
            for field in ("label", "block_title", "text_ua", "text_ru", "body_ua", "body_ru"):
                value = defaults.get(field, "")
                if value and not getattr(obj, field):
                    setattr(obj, field, value)
                    changed = True
            new_label = defaults.get("label", "")
            if (
                data.get("is_faq")
                and new_label.startswith("FAQ:")
                and obj.label
                and not obj.label.startswith("FAQ:")
            ):
                obj.label = new_label
                changed = True
            # Оновлювати назву блоку й роль поля з шаблону (не затирає тексти UA/RU)
            if defaults.get("block_title") and obj.block_title != defaults["block_title"]:
                obj.block_title = defaults["block_title"]
                changed = True
            if defaults.get("label") and (
                obj.label.startswith("Паспорт")
                or obj.label == obj.text_ua[:120]
                or not obj.label.startswith(("Заголовок:", "Текст", "FAQ"))
            ):
                # підтягнути зрозуміліші label з sync, якщо старі «сирі»
                if defaults["label"] != obj.label and defaults["label"].startswith(
                    ("Заголовок:", "Текст", "FAQ")
                ):
                    obj.label = defaults["label"]
                    changed = True
            if defaults.get("sort_order") and obj.sort_order != defaults["sort_order"]:
                obj.sort_order = defaults["sort_order"]
                changed = True
            if changed:
                obj.save()
                return "filled"
        return "skipped"
