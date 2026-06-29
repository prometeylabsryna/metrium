from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from src.core.models import SitePhone, SiteSettings
from src.core.services import clear_site_cache


@receiver(post_save, sender=SiteSettings)
@receiver(post_delete, sender=SiteSettings)
@receiver(post_save, sender=SitePhone)
@receiver(post_delete, sender=SitePhone)
def invalidate_site_cache(sender, **kwargs):
    clear_site_cache()
