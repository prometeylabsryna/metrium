from django.db import migrations


COMMON_REDIRECTS = (
    ("/uk", "/", 301),
    ("/en", "/", 301),
    ("/teknichnyj-pasport-na-budynok", "/tehnichnyj-pasport-na-budynok/", 301),
)


def add_common_redirects(apps, schema_editor):
    RedirectRule = apps.get_model("redirects", "RedirectRule")
    for source_path, target_url, status_code in COMMON_REDIRECTS:
        RedirectRule.objects.update_or_create(
            source_path=source_path,
            defaults={
                "target_url": target_url,
                "status_code": status_code,
                "is_active": True,
                "source": "manual",
            },
        )


def remove_common_redirects(apps, schema_editor):
    RedirectRule = apps.get_model("redirects", "RedirectRule")
    RedirectRule.objects.filter(
        source_path__in=[source for source, _, _ in COMMON_REDIRECTS],
        source="manual",
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("redirects", "0002_deactivate_ru_home_redirect"),
    ]

    operations = [
        migrations.RunPython(add_common_redirects, remove_common_redirects),
    ]
