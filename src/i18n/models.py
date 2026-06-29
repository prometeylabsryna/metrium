from django.db import models


class Language(models.TextChoices):
    UA = "ua", "Українська"
    RU = "ru", "Русский"


def language_prefix(language: str) -> str:
    return "/ru" if language == Language.RU else ""
