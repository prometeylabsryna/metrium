import re

from django.db import models
from django.utils.html import strip_tags

from src.i18n.models import Language, language_prefix


class BlogPost(models.Model):
    wp_id = models.PositiveIntegerField(null=True, blank=True, unique=True)
    slug = models.SlugField(max_length=200)
    title = models.CharField(max_length=500)
    language = models.CharField(max_length=5, choices=Language.choices, default=Language.UA)
    translation_group_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    excerpt = models.TextField(blank=True)
    body = models.TextField(blank=True)
    featured_image = models.ImageField(upload_to="blog/", blank=True, max_length=500)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-published_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["slug", "language"],
                name="unique_blog_slug_per_language",
            )
        ]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        prefix = language_prefix(self.language)
        return f"{prefix}/blogs/{self.slug}/"

    def get_body_html(self) -> str:
        """Виправляє артефакти імпорту WordPress (\\r\\n → rn) у HTML-контенті."""
        body = self.body
        body = body.replace("</br>", "")
        body = body.replace("<br></br>", "<br />")
        body = body.replace("rnrn", "<br /><br />")
        body = re.sub(r"rn(?=[<\t])", "", body)
        body = re.sub(r"rn(?=[А-ЯІЇЄҐA-Z])", "<br />", body)
        body = re.sub(r"rn", " ", body)
        return body.strip()

    def get_display_excerpt(self, word_limit: int = 22) -> str:
        if self.excerpt.strip():
            return self.excerpt.strip()
        text = strip_tags(self.body)
        text = re.sub(r"\s+", " ", text).strip()
        words = text.split()
        if len(words) <= word_limit:
            return text
        return " ".join(words[:word_limit]) + " [...]"

    def get_translation(self, language: str) -> "BlogPost | None":
        if not self.translation_group_id:
            return None
        return BlogPost.objects.filter(
            translation_group_id=self.translation_group_id,
            language=language,
            is_published=True,
        ).first()
