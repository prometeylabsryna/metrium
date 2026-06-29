from django.core.management.base import BaseCommand

from src.cms.models import HomeServiceCard, HomeStatItem, HomeWhyItem, PageSection
from src.core.models import SitePhone, SiteSettings


class Command(BaseCommand):
    help = "Заповнює адмінку початковим контентом сайту"

    def handle(self, *args, **options):
        settings_obj, created = SiteSettings.objects.get_or_create(pk=1)
        if created:
            self.stdout.write("Створено SiteSettings")

        if not settings_obj.phones.exists():
            SitePhone.objects.bulk_create(
                [
                    SitePhone(
                        settings=settings_obj,
                        tel_href="tel:0673986200",
                        display="067-398-62-00",
                        sort_order=0,
                    ),
                    SitePhone(
                        settings=settings_obj,
                        tel_href="tel:0500672060",
                        display="050-067-20-60",
                        sort_order=1,
                    ),
                ]
            )
            self.stdout.write("Додано телефони")

        if not HomeServiceCard.objects.exists():
            cards = [
                (
                    "Технічний паспорт на квартиру",
                    "Технический паспорт на квартиру",
                    "Для продажу, іпотеки, реєстрації права власності та перепланування",
                    "Для продажи, ипотеки, регистрации права собственности и перепланировки",
                    "/tehnichni-pasporty-bti/",
                ),
                (
                    "Технічний паспорт на будинок",
                    "Технический паспорт на дом",
                    "Для приватного будинку, дачі або садового будинку. Виїзд по Київщині",
                    "Для частного дома, дачи или садового дома. Выезд по Киевской области",
                    "/tehnichni-pasporty-bti/",
                ),
                (
                    "Технічний паспорт на гараж",
                    "Технический паспорт на гараж",
                    "Гараж, паркувальне місце або боксовий гараж — оформляємо всі типи",
                    "Гараж, парковочное место или боксовый гараж — оформляем все типы",
                    "/tehnichni-pasporty-bti/",
                ),
                (
                    "Легалізація самочинного будівництва",
                    "Легализация самовольного строительства",
                    "Узаконення незаконних будівель, добудов та реконструкцій",
                    "Узаконивание незаконных строений, пристроек и реконструкций",
                    "/legalizatsiya-neruhomosti/",
                ),
                (
                    "Звіт/Висновок про технічне обстеження",
                    "Отчет/Заключение о техническом обследовании",
                    "Офіційний висновок про технічний стан будівлі для будь-яких цілей",
                    "Официальное заключение о техническом состоянии здания для любых целей",
                    "/vysnovky-bti/",
                ),
                (
                    "Присвоєння поштової адреси",
                    "Присвоение почтового адреса",
                    "Офіційне присвоєння або підтвердження поштової адреси об'єкту нерухомості",
                    "Официальное присвоение или подтвержение почтового адреса объекту недвижимости",
                    "/dozvilna-dokumentatsiya/",
                ),
            ]
            HomeServiceCard.objects.bulk_create(
                [
                    HomeServiceCard(
                        title_ua=title_ua,
                        title_ru=title_ru,
                        description_ua=desc_ua,
                        description_ru=desc_ru,
                        url=url,
                        sort_order=index,
                    )
                    for index, (title_ua, title_ru, desc_ua, desc_ru, url) in enumerate(cards)
                ]
            )
            self.stdout.write(f"Додано {len(cards)} карток послуг")

        if not HomeWhyItem.objects.exists():
            items = [
                (
                    "Швидкість",
                    "Скорость",
                    "Всі проєкти виконуються оперативно, з високою якістю та без зайвих затримок.",
                    "Все проекты выполняются оперативно, с высоким качеством и без лишних задержек.",
                ),
                (
                    "Сертифікація",
                    "Сертификация",
                    "Найкращі професіонали, обладнання та інструменти, що пройшли відповідну сертифікацію.",
                    "Лучшие профессионалы, оборудование и инструменты, прошедшие соответствующую сертификацию.",
                ),
                (
                    "Досвід",
                    "Опыт",
                    "Тисячі об'єктів і десятиріччя плідної праці допоможуть вирішити питання будь-якої складності.",
                    "Тысячи объектов и десятилетия плодотворной работы помогут решить вопросы любой сложности.",
                ),
                (
                    "Зручність",
                    "Удобство",
                    "Процес від замовлення до отримання результату, організований з урахуванням саме Ваших потреб.",
                    "Процесс от заказа до получения результата организован с учетом именно Ваших потребностей.",
                ),
            ]
            HomeWhyItem.objects.bulk_create(
                [
                    HomeWhyItem(
                        title_ua=title_ua,
                        title_ru=title_ru,
                        text_ua=text_ua,
                        text_ru=text_ru,
                        sort_order=index,
                    )
                    for index, (title_ua, title_ru, text_ua, text_ru) in enumerate(items)
                ]
            )
            self.stdout.write(f"Додано {len(items)} переваг")

        if not HomeStatItem.objects.exists():
            stats = [
                ("12", "років досвіду", "лет опыта"),
                ("10", "філій по Києву та Київській області", "филиалов по Киеву и Киевской области"),
                ("5000+", "успішних проєктів", "успешных проектов"),
                ("20+", "об'єктів на тиждень", "объектов в неделю"),
            ]
            HomeStatItem.objects.bulk_create(
                [
                    HomeStatItem(value=value, label_ua=label_ua, label_ru=label_ru, sort_order=index)
                    for index, (value, label_ua, label_ru) in enumerate(stats)
                ]
            )
            self.stdout.write(f"Додано {len(stats)} статистик")

        sections = [
            ("home", "services.label", "Наші послуги / Наши услуги", "Наші послуги", "Наши услуги"),
            ("home", "services.title", "Заголовок послуг", "Послуги", "Услуги"),
            ("home", "calc.label", "Калькулятор: мітка", "Онлайн-калькулятор", "Онлайн-калькулятор"),
            ("home", "calc.title", "Калькулятор: заголовок", "Вартість техпаспорта БТІ", "Стоимость техпаспорта БТИ"),
            ("home", "why.title", "Чому ми", "Чому варто обрати наше БТІ?", "Почему стоит выбрать наше БТИ?"),
            ("home", "about.accent", "Про нас: акцент", "ПРИВАТНЕ БТІ METRIUM", "ЧАСТНОЕ БТИ METRIUM"),
        ]
        created_sections = 0
        for page_slug, section_key, label, text_ua, text_ru in sections:
            _, created = PageSection.objects.get_or_create(
                page_slug=page_slug,
                section_key=section_key,
                defaults={"label": label, "text_ua": text_ua, "text_ru": text_ru},
            )
            if created:
                created_sections += 1

        self.stdout.write(self.style.SUCCESS(f"Готово. Нових секцій: {created_sections}"))
