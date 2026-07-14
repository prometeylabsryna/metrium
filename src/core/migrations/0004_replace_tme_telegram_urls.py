from django.db import migrations


OLD_PREFIX = "https://t.me/"
NEW_PREFIX = "https://telegram.me/"


def forwards(apps, schema_editor):
    SiteSettings = apps.get_model("core", "SiteSettings")
    for row in SiteSettings.objects.filter(telegram__startswith=OLD_PREFIX).iterator():
        row.telegram = NEW_PREFIX + row.telegram[len(OLD_PREFIX) :]
        row.save(update_fields=["telegram"])


def backwards(apps, schema_editor):
    SiteSettings = apps.get_model("core", "SiteSettings")
    for row in SiteSettings.objects.filter(telegram__startswith=NEW_PREFIX).iterator():
        row.telegram = OLD_PREFIX + row.telegram[len(NEW_PREFIX) :]
        row.save(update_fields=["telegram"])


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_telegram_default_url"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
