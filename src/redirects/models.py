from django.db import models


class RedirectRule(models.Model):
    source_path = models.CharField(max_length=500, unique=True, db_index=True)
    target_url = models.CharField(max_length=500, blank=True)
    status_code = models.PositiveSmallIntegerField(default=301)
    is_active = models.BooleanField(default=True)
    source = models.CharField(
        max_length=20,
        choices=[
            ("htaccess", "htaccess 410"),
            ("eps", "EPS 301"),
            ("manual", "Manual"),
        ],
        default="manual",
    )

    class Meta:
        ordering = ["source_path"]

    def __str__(self) -> str:
        return f"{self.status_code} {self.source_path}"
