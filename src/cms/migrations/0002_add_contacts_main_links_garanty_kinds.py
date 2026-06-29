from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pageblock',
            name='kind',
            field=models.CharField(
                choices=[
                    ('banner', 'Банер'),
                    ('text', 'Текст'),
                    ('calculator', 'Калькулятор'),
                    ('services', 'Послуги'),
                    ('price_list', 'Прайс'),
                    ('lead_form', 'Форма заявки'),
                    ('faq', 'FAQ'),
                    ('reviews', 'Відгуки'),
                    ('seo_text', 'SEO текст'),
                    ('map', 'Карта'),
                    ('video', 'Відео'),
                    ('gallery', 'Галерея'),
                    ('steps', 'Кроки'),
                    ('brands', 'Бренди'),
                    ('contacts', 'Контакти'),
                    ('main_links', 'Інфо-посилання'),
                    ('garanty', 'Гарантія'),
                    ('html', 'HTML (legacy)'),
                ],
                max_length=30,
            ),
        ),
    ]
