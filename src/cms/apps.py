from django.apps import AppConfig


class CmsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "src.cms"
    label = "cms"

    def ready(self):
        from src.cms import signals  # noqa: F401
