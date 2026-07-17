# Generated manually on 2026-07-17

from django.db import migrations

URL_FIXES = {
    "Технічний паспорт на квартиру": (
        "/tehnichni-pasporty-bti/",
        "/tehnichnyj-pasport-na-kvartyru/",
    ),
    "Технічний паспорт на будинок": (
        "/tehnichni-pasporty-bti/",
        "/tehnichnyj-pasport-na-budynok/",
    ),
    "Технічний паспорт на гараж": (
        "/tehnichni-pasporty-bti/",
        "/tehnichnyj-pasport-na-garazh/",
    ),
}


def fix_urls(apps, schema_editor):
    """Виправляє картки послуг на головній, що всі вели на спільну
    сторінку /tehnichni-pasporty-bti/ замість власних сторінок з
    відповідним типом об'єкта в калькуляторі."""
    HomeServiceCard = apps.get_model("cms", "HomeServiceCard")
    for title_ua, (old_url, new_url) in URL_FIXES.items():
        HomeServiceCard.objects.filter(title_ua=title_ua, url=old_url).update(url=new_url)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("cms", "0005_pagesection_siteimage_owner_link"),
    ]

    operations = [
        migrations.RunPython(fix_urls, noop),
    ]
