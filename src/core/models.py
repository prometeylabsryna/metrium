from django.db import models


class SiteSettings(models.Model):
    site_name = models.CharField("Назва сайту", max_length=100, default="Metrium")
    logo = models.ImageField("Логотип", upload_to="site/", blank=True)
    logo_alt_ua = models.CharField("Alt логотипу (UA)", max_length=200, default="Метріум БТІ")
    logo_alt_ru = models.CharField("Alt логотипу (RU)", max_length=200, default="Метриум БТИ")

    schedule_header_ua = models.CharField(
        "Графік у шапці (UA)",
        max_length=200,
        default="Пн-Пт: 08:00–21:00 | Сб: 09:00–18:00",
    )
    schedule_header_ru = models.CharField(
        "Графік у шапці (RU)",
        max_length=200,
        default="Пн-Пт: 08:00–21:00 | Сб: 09:00–18:00",
    )
    schedule_weekdays_ua = models.CharField("Пн-Пт (UA)", max_length=100, default="Пн-Пт: 08:00 – 21:00")
    schedule_weekdays_ru = models.CharField("Пн-Пт (RU)", max_length=100, default="Пн-Пт: 08:00 – 21:00")
    schedule_saturday_ua = models.CharField("Субота (UA)", max_length=100, default="Сб: 09:00 – 18:00")
    schedule_saturday_ru = models.CharField("Субота (RU)", max_length=100, default="Сб: 09:00 – 18:00")
    schedule_sunday_ua = models.CharField("Неділя (UA)", max_length=100, default="Нд: Вихідний")
    schedule_sunday_ru = models.CharField("Неділя (RU)", max_length=100, default="Вс: Выходной")

    email = models.EmailField("Email", default="pruvatnebti@gmail.com")
    region_label_ua = models.CharField(
        "Регіон (UA)",
        max_length=200,
        default="м. Київ та Київська область",
    )
    region_label_ru = models.CharField(
        "Регіон (RU)",
        max_length=200,
        default="г. Киев и Киевская область",
    )

    telegram = models.URLField("Telegram", default="https://telegram.me/metriumbti", blank=True)
    viber = models.CharField("Viber", max_length=300, default="viber://chat?number=%2B380673986200", blank=True)
    whatsapp = models.URLField("WhatsApp", default="https://wa.me/380673986200", blank=True)
    instagram = models.URLField("Instagram", default="https://www.instagram.com/pruvatnebti", blank=True)
    facebook = models.URLField(
        "Facebook",
        default="https://www.facebook.com/profile.php?id=61584165429803",
        blank=True,
    )

    footer_consult_title_ua = models.CharField(
        "Футер: заголовок форми (UA)",
        max_length=200,
        default="Отримати консультацію зараз",
    )
    footer_consult_title_ru = models.CharField(
        "Футер: заголовок форми (RU)",
        max_length=200,
        default="Получить консультацию сейчас",
    )
    footer_rights_ua = models.CharField("Футер: права (UA)", max_length=200, default="Всі права захищено.")
    footer_rights_ru = models.CharField("Футер: права (RU)", max_length=200, default="Все права защищены.")
    privacy_url = models.CharField("Посилання політики", max_length=300, blank=True, default="#")
    privacy_label_ua = models.CharField(
        "Політика конфіденційності (UA)",
        max_length=100,
        default="Політика конфіденційності",
    )
    privacy_label_ru = models.CharField(
        "Політика конфіденційності (RU)",
        max_length=100,
        default="Политика конфиденциальности",
    )

    hero_image_desktop = models.ImageField(
        "Hero: фото (десктоп)",
        upload_to="hero/",
        blank=True,
        help_text="Рекомендовано 1920×800 px",
    )
    hero_image_mobile = models.ImageField(
        "Hero: фото (мобільний)",
        upload_to="hero/",
        blank=True,
        help_text="Рекомендовано 768×900 px",
    )
    hero_title_ua = models.TextField(
        "Hero: заголовок (UA)",
        default="Бюро Технічної\nІнвентаризації",
    )
    hero_title_ru = models.TextField(
        "Hero: заголовок (RU)",
        default="Бюро Технической\nИнвентаризации",
    )
    hero_subtitle_ua = models.TextField(
        "Hero: підзаголовок (UA)",
        default="Послуги БТІ без прихованих платежів!\nШвидко, зручно, надійно!",
    )
    hero_subtitle_ru = models.TextField(
        "Hero: підзаголовок (RU)",
        default="Услуги БТИ без скрытых платежей!\nБыстро, удобно, надежно!",
    )
    hero_form_title_ua = models.CharField(
        "Hero: заголовок форми (UA)",
        max_length=300,
        default="Швидке замовлення технічного паспорта БТІ",
    )
    hero_form_title_ru = models.CharField(
        "Hero: заголовок форми (RU)",
        max_length=300,
        default="Быстрый заказ технического паспорта БТИ",
    )
    hero_form_text_ua = models.TextField(
        "Hero: текст форми (UA)",
        default="Для замовлення залиште Ваш номер телефону і наша команда спеціалістів з Вами зв'яжеться",
    )
    hero_form_text_ru = models.TextField(
        "Hero: текст форми (RU)",
        default="Для заказа оставьте Ваш номер телефона и наша команда специалистов с Вами свяжется",
    )

    class Meta:
        verbose_name = "Налаштування сайту"
        verbose_name_plural = "Налаштування сайту"

    def __str__(self) -> str:
        return "Налаштування сайту"

    def text(self, field_base: str, language: str) -> str:
        suffix = "_ru" if language == "ru" else "_ua"
        return getattr(self, f"{field_base}{suffix}", "")


class SitePhone(models.Model):
    settings = models.ForeignKey(
        SiteSettings,
        on_delete=models.CASCADE,
        related_name="phones",
        verbose_name="Налаштування",
    )
    tel_href = models.CharField("Посилання tel:", max_length=30, default="tel:0673986200")
    display = models.CharField("Відображення", max_length=30, default="067-398-62-00")
    sort_order = models.PositiveSmallIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Активний", default=True)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Телефон"
        verbose_name_plural = "Телефони"

    def __str__(self) -> str:
        return self.display


class Office(models.Model):
    city = models.CharField(max_length=100, verbose_name="Місто")
    title = models.CharField(max_length=200, verbose_name="Назва (відображується)")
    address = models.CharField(max_length=300, blank=True, verbose_name="Адреса")
    lat = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True, verbose_name="Широта")
    lng = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True, verbose_name="Довгота")
    map_embed_url = models.TextField(blank=True, verbose_name="URL embed карти")
    map_link = models.URLField(max_length=500, blank=True, verbose_name="Google Maps посилання")
    waze_link = models.URLField(max_length=500, blank=True, verbose_name="Waze посилання")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="Порядок сортування")
    is_active = models.BooleanField(default=True, verbose_name="Активний")
    is_main = models.BooleanField(default=False, verbose_name="Головний офіс")

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Офіс"
        verbose_name_plural = "Офіси"

    def __str__(self) -> str:
        return self.title

    @property
    def display_label(self) -> str:
        title = self.title.replace(" (головний офіс)", "")
        if " — " in title:
            city, address = title.split(" — ", 1)
            return f"{city}, {address}"
        return title

    @property
    def lat_str(self) -> str:
        if self.lat is None:
            return ""
        return format(self.lat, "f")

    @property
    def lng_str(self) -> str:
        if self.lng is None:
            return ""
        return format(self.lng, "f")

    @property
    def coordinates_str(self) -> str:
        if not self.lat_str or not self.lng_str:
            return ""
        return f"{self.lat_str},{self.lng_str}"
