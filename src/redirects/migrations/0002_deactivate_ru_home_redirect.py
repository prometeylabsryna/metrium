from django.db import migrations


def deactivate_ru_home_redirect(apps, schema_editor):
    RedirectRule = apps.get_model("redirects", "RedirectRule")
    RedirectRule.objects.filter(source_path="/ru", target_url="/golovna/").update(is_active=False)


class Migration(migrations.Migration):

    dependencies = [
        ("redirects", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(deactivate_ru_home_redirect, migrations.RunPython.noop),
    ]
