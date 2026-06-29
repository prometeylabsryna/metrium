from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from src.cms.models import HomeServiceCard, HomeStatItem, HomeWhyItem, PageSection, SiteImage
from src.cms.services import clear_image_cache, clear_section_cache


@receiver(post_save, sender=PageSection)
@receiver(post_delete, sender=PageSection)
def invalidate_section_cache(sender, instance, **kwargs):
    clear_section_cache(instance.page_slug, instance.section_key)


@receiver(post_save, sender=SiteImage)
@receiver(post_delete, sender=SiteImage)
def invalidate_image_cache(sender, instance, **kwargs):
    clear_image_cache(instance.page_slug, instance.image_key)
