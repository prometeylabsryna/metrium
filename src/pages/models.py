from django.db import models

from src.i18n.models import Language, language_prefix


class StaticPage(models.Model):
    wp_id = models.PositiveIntegerField(null=True, blank=True, unique=True)
    slug = models.SlugField(max_length=200)
    title = models.CharField(max_length=500)
    language = models.CharField(max_length=5, choices=Language.choices, default=Language.UA)
    translation_group_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    template_key = models.CharField(max_length=100, blank=True)
    use_block_builder = models.BooleanField(default=True)
    is_published = models.BooleanField(default=False)
    is_home = models.BooleanField(default=False)
    location = models.CharField(max_length=100, blank=True)
    body_legacy = models.TextField(blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["slug"]
        constraints = [
            models.UniqueConstraint(
                fields=["slug", "language"],
                name="unique_page_slug_per_language",
            )
        ]

    def __str__(self) -> str:
        return f"[{self.language}] {self.title}"

    def get_absolute_url(self) -> str:
        prefix = language_prefix(self.language)
        if self.is_home or self.slug in ("home", ""):
            return f"{prefix}/" if prefix else "/"
        return f"{prefix}/{self.slug}/"

    def get_translation(self, language: str) -> "StaticPage | None":
        if not self.translation_group_id:
            return None
        return (
            StaticPage.objects.filter(
                translation_group_id=self.translation_group_id,
                language=language,
                is_published=True,
            )
            .first()
        )
