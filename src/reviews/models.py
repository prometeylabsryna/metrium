from django.db import models


class Review(models.Model):
    name = models.CharField(max_length=200, verbose_name="Ім'я")
    text = models.TextField(verbose_name="Текст відгуку")
    rating = models.PositiveSmallIntegerField(
        default=5,
        choices=[(i, str(i)) for i in range(1, 6)],
        verbose_name="Рейтинг",
    )
    is_published = models.BooleanField(default=False, verbose_name="Опублікований")
    is_featured = models.BooleanField(
        default=False,
        verbose_name="Показувати на головній (слайдер)",
    )
    source = models.CharField(
        max_length=30,
        choices=[("google", "Google"), ("site", "Сайт"), ("other", "Інше")],
        default="site",
        verbose_name="Джерело",
    )
    published_at = models.DateField(null=True, blank=True, verbose_name="Дата відгуку")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]
        verbose_name = "Відгук"
        verbose_name_plural = "Відгуки"

    def __str__(self) -> str:
        return f"{self.name} ({self.rating}★)"

    def rating_display(self) -> str:
        return f"{self.rating}.0"
