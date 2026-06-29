from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class BlockKind(models.TextChoices):
    BANNER = "banner", "Банер"
    TEXT = "text", "Текст"
    CALCULATOR = "calculator", "Калькулятор"
    SERVICES = "services", "Послуги"
    PRICE_LIST = "price_list", "Прайс"
    LEAD_FORM = "lead_form", "Форма заявки"
    FAQ = "faq", "FAQ"
    REVIEWS = "reviews", "Відгуки"
    SEO_TEXT = "seo_text", "SEO текст"
    MAP = "map", "Карта"
    VIDEO = "video", "Відео"
    GALLERY = "gallery", "Галерея"
    STEPS = "steps", "Кроки"
    BRANDS = "brands", "Бренди"
    CONTACTS = "contacts", "Контакти"
    MAIN_LINKS = "main_links", "Інфо-посилання"
    GARANTY = "garanty", "Гарантія"
    HTML = "html", "HTML (legacy)"


class PageBlock(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    owner = GenericForeignKey("content_type", "object_id")

    kind = models.CharField(max_length=30, choices=BlockKind.choices)
    sort_order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)
    css_anchor = models.SlugField(max_length=100, blank=True)

    heading = models.TextField(blank=True)
    body = models.TextField(blank=True)
    image = models.ImageField(upload_to="blocks/", blank=True)
    image_alt = models.CharField(max_length=255, blank=True)
    button_text = models.CharField(max_length=200, blank=True)
    button_url = models.CharField(max_length=500, blank=True)
    extra_data = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self) -> str:
        return f"{self.kind} #{self.pk}"


class PageSection(models.Model):
    PAGE_CHOICES = [
        ("global", "Загальне"),
        ("home", "Головна"),
        ("header", "Шапка"),
        ("footer", "Футер"),
        ("about", "Про нас"),
        ("contacts", "Контакти"),
        ("blog", "Блог"),
        ("reviews", "Відгуки"),
        ("tehnichni-pasporty-bti", "Технічні паспорти"),
        ("bti-cina", "Ціна БТІ"),
        ("vvedennya-v-ekspluatatsiyu", "Введення в експлуатацію"),
        ("legalizatsiya-neruhomosti", "Легалізація"),
        ("dozvilna-dokumentatsiya", "Дозвільна документація"),
        ("zemelna-dokumentatsiya", "Земельна документація"),
        ("dovidky", "Довідки"),
        ("poslugy-kyiv", "Послуги Київ"),
        ("neobhidni-dokumenty", "Необхідні документи"),
        ("tehnichnyj-pasport-na-kvartyru", "Паспорт на квартиру"),
        ("tehnichnyj-pasport-na-budynok", "Паспорт на будинок"),
        ("elektronnyj-tehnichnyj-pasport", "Електронний паспорт"),
        ("tehnichnyj-pasport-na-budivlyu", "Паспорт на будівлю"),
        ("tehnichnyj-pasport-na-garazh", "Паспорт на гараж"),
        ("tehnichnyj-pasport-na-nezhytlove-prymischennya", "Нежитлове приміщення"),
        ("tehnichnyj-pasport-na-bagato-kvartyrnyj-budynok", "Багатоквартирний будинок"),
        ("tehnichna-inventaryzatsiya", "Інвентаризація"),
        ("kadastrovyj-nomer", "Кадастровий номер"),
        ("vytiah-dzk", "Витяг ДЗК"),
        ("vysnovky-bti", "Висновки БТІ"),
        ("kyiv-oblast", "Київська область"),
    ]

    page_slug = models.CharField("Сторінка", max_length=100, choices=PAGE_CHOICES)
    section_key = models.SlugField("Ключ секції", max_length=100)
    label = models.CharField("Назва в адмінці", max_length=200)

    text_ua = models.TextField("Текст (UA)", blank=True)
    text_ru = models.TextField("Текст (RU)", blank=True)
    body_ua = models.TextField("HTML / довгий текст (UA)", blank=True)
    body_ru = models.TextField("HTML / довгий текст (RU)", blank=True)

    image = models.ImageField("Зображення", upload_to="sections/", blank=True)
    image_alt_ua = models.CharField("Alt зображення (UA)", max_length=255, blank=True)
    image_alt_ru = models.CharField("Alt зображення (RU)", max_length=255, blank=True)
    icon = models.ImageField("Іконка", upload_to="sections/icons/", blank=True)
    url = models.CharField("Посилання", max_length=500, blank=True)

    sort_order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Активна", default=True)

    class Meta:
        ordering = ["page_slug", "sort_order", "section_key"]
        verbose_name = "Текст сторінки"
        verbose_name_plural = "Тексти сторінок"
        constraints = [
            models.UniqueConstraint(
                fields=["page_slug", "section_key"],
                name="unique_page_section_key",
            )
        ]

    def __str__(self) -> str:
        return f"{self.get_page_slug_display()} · {self.label}"

    def localized_text(self, language: str) -> str:
        return self.text_ru if language == "ru" else self.text_ua

    def localized_body(self, language: str) -> str:
        return self.body_ru if language == "ru" else self.body_ua

    def localized_image_alt(self, language: str) -> str:
        return self.image_alt_ru if language == "ru" else self.image_alt_ua


class HomeServiceCard(models.Model):
    title_ua = models.CharField("Заголовок (UA)", max_length=300)
    title_ru = models.CharField("Заголовок (RU)", max_length=300)
    description_ua = models.TextField("Опис (UA)", blank=True)
    description_ru = models.TextField("Опис (RU)", blank=True)
    icon = models.ImageField("Іконка", upload_to="home/services/", blank=True)
    url = models.CharField("Посилання", max_length=300)
    sort_order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Активна", default=True)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Картка послуги (головна)"
        verbose_name_plural = "Картки послуг (головна)"

    def __str__(self) -> str:
        return self.title_ua


class HomeWhyItem(models.Model):
    title_ua = models.CharField("Заголовок (UA)", max_length=200)
    title_ru = models.CharField("Заголовок (RU)", max_length=200)
    text_ua = models.TextField("Текст (UA)")
    text_ru = models.TextField("Текст (RU)")
    icon = models.ImageField("Іконка", upload_to="home/why/", blank=True)
    sort_order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Активна", default=True)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Перевага (головна)"
        verbose_name_plural = "Переваги (головна)"

    def __str__(self) -> str:
        return self.title_ua


class HomeStatItem(models.Model):
    value = models.CharField("Цифра", max_length=30)
    label_ua = models.CharField("Підпис (UA)", max_length=200)
    label_ru = models.CharField("Підпис (RU)", max_length=200)
    sort_order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Активна", default=True)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Статистика (головна)"
        verbose_name_plural = "Статистика (головна)"

    def __str__(self) -> str:
        return f"{self.value} — {self.label_ua}"


class SiteImage(models.Model):
    PAGE_CHOICES = PageSection.PAGE_CHOICES

    page_slug = models.CharField("Сторінка", max_length=100, choices=PAGE_CHOICES)
    image_key = models.SlugField("Ключ зображення", max_length=100)
    label = models.CharField("Назва в адмінці", max_length=200)

    image = models.ImageField("Зображення", upload_to="site-images/", blank=True)
    image_mobile = models.ImageField("Зображення (мобільне)", upload_to="site-images/", blank=True)
    image_alt_ua = models.CharField("Alt (UA)", max_length=255, blank=True)
    image_alt_ru = models.CharField("Alt (RU)", max_length=255, blank=True)

    fallback_static = models.CharField(
        "Fallback static (desktop)",
        max_length=300,
        blank=True,
        help_text="Шлях від static/, напр. images/kata/kvartiry.webp",
    )
    fallback_static_mobile = models.CharField(
        "Fallback static (mobile)",
        max_length=300,
        blank=True,
    )

    sort_order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Активне", default=True)

    class Meta:
        ordering = ["page_slug", "sort_order", "image_key"]
        verbose_name = "Зображення сайту"
        verbose_name_plural = "Зображення сайту"
        constraints = [
            models.UniqueConstraint(
                fields=["page_slug", "image_key"],
                name="unique_site_image_key",
            )
        ]

    def __str__(self) -> str:
        return f"{self.get_page_slug_display()} · {self.label}"

    def localized_alt(self, language: str) -> str:
        return self.image_alt_ru if language == "ru" else self.image_alt_ua
