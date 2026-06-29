from django.db import models


class LeadSubmission(models.Model):
    class LeadType(models.TextChoices):
        PHONE = "phone", "Телефон"
        CALCULATOR = "calculator", "Калькулятор"
        REVIEW = "review", "Відгук"

    lead_type = models.CharField(max_length=20, choices=LeadType.choices)
    name = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    page_title = models.CharField(max_length=500, blank=True)
    payload = models.JSONField(default=dict, blank=True)
    channel = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.lead_type} {self.phone or self.name}"
