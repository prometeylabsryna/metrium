"""
Management command: populate_archive_data
Заповнює базу даних даними з WordPress-архіву:
  - 14 офісів з координатами
  - SEO metadata для сторінок contacts та about
"""
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from src.core.models import Office
from src.pages.models import StaticPage
from src.seo.models import SeoMetadata


OFFICES = [
    {
        "city": "kiev",
        "title": "Київ — вул. Салютна, 15",
        "address": "вул. Салютна, 15",
        "lat": "50.472051",
        "lng": "30.408564",
        "sort_order": 1,
        "is_main": False,
    },
    {
        "city": "kiev",
        "title": "Київ — просп. Правди, 70",
        "address": "просп. Правди, 70",
        "lat": "50.504739",
        "lng": "30.427647",
        "sort_order": 2,
        "is_main": False,
    },
    {
        "city": "kiev",
        "title": "Київ — вул. Будівельників, 36",
        "address": "вул. Будівельників, 36",
        "lat": "50.453055",
        "lng": "30.611864",
        "sort_order": 3,
        "is_main": False,
    },
    {
        "city": "kiev",
        "title": "Київ — пров. Киянівський, 7",
        "address": "пров. Киянівський, 7",
        "lat": "50.457164",
        "lng": "30.506647",
        "sort_order": 4,
        "is_main": False,
    },
    {
        "city": "kiev",
        "title": "Київ — просп. Червоної Калини, 26",
        "address": "просп. Червоної Калини, 26",
        "lat": "50.508298",
        "lng": "30.608653",
        "sort_order": 5,
        "is_main": False,
    },
    {
        "city": "kiev",
        "title": "Київ — просп. Берестейський, 67",
        "address": "просп. Берестейський, 67",
        "lat": "50.458054",
        "lng": "30.405893",
        "sort_order": 6,
        "is_main": False,
    },
    {
        "city": "bucha",
        "title": "Буча — вул. Енергетиків, 8",
        "address": "вул. Енергетиків, 8",
        "lat": "50.551193",
        "lng": "30.212097",
        "sort_order": 7,
        "is_main": False,
    },
    {
        "city": "irpin",
        "title": "Ірпінь — вул. Стельмаха, 9а (головний офіс)",
        "address": "вул. Стельмаха, 9а",
        "lat": "50.515643",
        "lng": "30.255479",
        "sort_order": 0,
        "is_main": True,
    },
    {
        "city": "bila_tserkva",
        "title": "Біла Церква — вул. Леваневського, 57",
        "address": "вул. Леваневського, 57",
        "lat": "49.785888",
        "lng": "30.157499",
        "sort_order": 9,
        "is_main": False,
    },
    {
        "city": "boryspil",
        "title": "Бориспіль — вул. Київський шлях, 4",
        "address": "вул. Київський шлях, 4",
        "lat": "50.359658",
        "lng": "30.935782",
        "sort_order": 10,
        "is_main": False,
    },
    {
        "city": "brovary",
        "title": "Бровари — вул. Героїв України, 16",
        "address": "вул. Героїв України, 16",
        "lat": "50.511796",
        "lng": "30.788646",
        "sort_order": 11,
        "is_main": False,
    },
    {
        "city": "vyshhorod",
        "title": "Вишгород — вул. Шолуденка, 1",
        "address": "вул. Шолуденка, 1",
        "lat": "50.587471",
        "lng": "30.494562",
        "sort_order": 12,
        "is_main": False,
    },
    {
        "city": "obuhiv",
        "title": "Обухів — вул. Каштанова, 16",
        "address": "вул. Каштанова, 16",
        "lat": "50.127960",
        "lng": "30.650143",
        "sort_order": 13,
        "is_main": False,
    },
    {
        "city": "fastiv",
        "title": "Фастів — вул. Соборна, 40а",
        "address": "вул. Соборна, 40а",
        "lat": "50.080121",
        "lng": "29.910502",
        "sort_order": 14,
        "is_main": False,
    },
]


SEO_DATA = {
    "contacts": {
        "seo_title": "Контакти Метріум БТІ — Ірпінь, Київ та Київська область",
        "seo_description": (
            "Адреси, телефони та графік роботи Метріум БТІ. "
            "Ірпінь, вул. Стельмаха 9а. Тел: 067-398-62-00. "
            "Виготовлення технічних паспортів БТІ по всій Київській області."
        ),
        "og_title": "Контакти Метріум БТІ",
        "og_description": "Знайдіть наш офіс в Ірпені або зателефонуйте: 067-398-62-00",
        "og_image_url": "https://metrium.com.ua/wp-content/uploads/2024/08/bti_logo.webp",
        "sitemap_priority": "0.7",
        "sitemap_changefreq": "monthly",
    },
    "about": {
        "seo_title": "Про нас — Метріум, приватне БТІ Київської області",
        "seo_description": (
            "Приватне підприємство Метріум — офіційна компанія з виготовлення "
            "технічних паспортів БТІ. Сертифіковані інвентаризатори. "
            "Ірпінь та вся Київська область. Досвід 10+ років."
        ),
        "og_title": "Про компанію Метріум БТІ",
        "og_description": (
            "Ліцензована компанія з виготовлення технічних паспортів. "
            "Керівник: Кравченко Олег Миколайович."
        ),
        "og_image_url": "https://metrium.com.ua/wp-content/uploads/2024/08/bti_logo.webp",
        "sitemap_priority": "0.6",
        "sitemap_changefreq": "monthly",
    },
}


class Command(BaseCommand):
    help = "Заповнює дані з WordPress-архіву: офіси та SEO"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Тільки показати що буде зроблено, без змін у БД",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        self._populate_offices(dry_run)
        self._populate_seo(dry_run)

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN — жодних змін не збережено"))
        else:
            self.stdout.write(self.style.SUCCESS("Готово! Дані з архіву успішно додано."))

    def _populate_offices(self, dry_run: bool) -> None:
        self.stdout.write("\n=== Офіси ===")
        existing_count = Office.objects.count()

        if existing_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"  В БД вже є {existing_count} офіс(ів). Пропускаємо (щоб скинути — видаліть існуючі записи)."
                )
            )
            return

        for data in OFFICES:
            if dry_run:
                self.stdout.write(f"  [DRY] Буде створено: {data['title']}")
                continue

            Office.objects.create(
                city=data["city"],
                title=data["title"],
                address=data["address"],
                lat=data["lat"],
                lng=data["lng"],
                sort_order=data["sort_order"],
                is_main=data["is_main"],
                is_active=True,
            )
            self.stdout.write(self.style.SUCCESS(f"  ✓ Додано: {data['title']}"))

        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(f"  Разом: {len(OFFICES)} офісів створено")
            )

    def _populate_seo(self, dry_run: bool) -> None:
        self.stdout.write("\n=== SEO metadata ===")
        ct = ContentType.objects.get_for_model(StaticPage)

        for slug, seo_fields in SEO_DATA.items():
            page = StaticPage.objects.filter(slug=slug, language="ua").first()

            if not page:
                # Create minimal page if not exists (for "about")
                if slug == "about":
                    if dry_run:
                        self.stdout.write(f"  [DRY] Буде створено сторінку slug='{slug}'")
                        self.stdout.write(f"  [DRY] SEO для '{slug}': {seo_fields['seo_title'][:60]}")
                        continue
                    else:
                        page = StaticPage.objects.create(
                            slug=slug,
                            title="Про нас",
                            language="ua",
                            is_published=True,
                            is_home=False,
                        )
                        self.stdout.write(self.style.SUCCESS(f"  ✓ Сторінку '{slug}' створено"))
                else:
                    self.stdout.write(
                        self.style.WARNING(f"  Сторінка slug='{slug}' не знайдена — пропускаємо")
                    )
                    continue

            seo = SeoMetadata.objects.filter(content_type=ct, object_id=page.pk).first()

            if seo and seo.seo_title:
                self.stdout.write(
                    f"  SEO для '{slug}' вже є: {seo.seo_title[:60]} — пропускаємо"
                )
                continue

            if dry_run:
                self.stdout.write(
                    f"  [DRY] SEO для '{slug}': {seo_fields['seo_title'][:60]}"
                )
                continue

            defaults = {k: v for k, v in seo_fields.items()}
            if seo:
                for k, v in defaults.items():
                    setattr(seo, k, v)
                seo.save()
                self.stdout.write(self.style.SUCCESS(f"  ✓ SEO оновлено для '{slug}'"))
            else:
                SeoMetadata.objects.create(
                    content_type=ct,
                    object_id=page.pk,
                    **defaults,
                )
                self.stdout.write(self.style.SUCCESS(f"  ✓ SEO створено для '{slug}'"))
