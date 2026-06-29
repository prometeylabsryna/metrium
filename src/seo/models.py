from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class SeoMetadata(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    seo_title = models.CharField(max_length=500, blank=True)
    seo_description = models.TextField(blank=True)
    keywords = models.CharField(max_length=500, blank=True)
    canonical_url = models.URLField(max_length=500, blank=True)
    robots_noindex = models.BooleanField(default=False)
    robots_nofollow = models.BooleanField(default=False)
    og_title = models.CharField(max_length=500, blank=True)
    og_description = models.TextField(blank=True)
    og_image_url = models.URLField(max_length=500, blank=True)
    twitter_title = models.CharField(max_length=500, blank=True)
    twitter_description = models.TextField(blank=True)
    schema_json = models.TextField(blank=True)
    sitemap_priority = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True)
    sitemap_changefreq = models.CharField(max_length=20, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["content_type", "object_id"],
                name="unique_seo_per_object",
            )
        ]

    def __str__(self) -> str:
        return self.seo_title or f"SEO #{self.pk}"
