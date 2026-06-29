from django.conf import settings

from src.i18n.models import Language
from src.seo.models import SeoMetadata


def get_seo_for_object(obj) -> SeoMetadata | None:
    if obj is None:
        return None
    return SeoMetadata.objects.filter(
        content_type__model=obj._meta.model_name,
        content_type__app_label=obj._meta.app_label,
        object_id=obj.pk,
    ).first()


def build_robots_directive(seo: SeoMetadata | None) -> str:
    if not seo:
        return "index, follow"
    parts = []
    parts.append("noindex" if seo.robots_noindex else "index")
    parts.append("nofollow" if seo.robots_nofollow else "follow")
    return ", ".join(parts)


def build_canonical_url(obj, seo: SeoMetadata | None, request) -> str:
    if seo and seo.canonical_url:
        return seo.canonical_url
    return request.build_absolute_uri(obj.get_absolute_url())


def hreflang_code(language: str) -> str:
    return language


def organization_schema() -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "url": settings.SITE_URL,
        "sameAs": [
            "https://www.instagram.com/pruvatnebti/",
            "https://www.facebook.com/profile.php?id=61584165429803",
            "https://t.me/metriumbti",
        ],
        "logo": f"{settings.SITE_URL}/wp-content/uploads/2024/08/bti_logo.webp",
        "image": f"{settings.SITE_URL}/wp-content/uploads/2024/08/bti_logo.webp",
        "name": "Метріум БТІ — технічні паспорти",
        "description": "Виготовлення технічних паспортів БТІ. Допомога у легалізації самочинного будівництва",
        "email": settings.LEADS_EMAIL,
        "telephone": "+380673986200",
        "priceRange": "₴₴",
        "openingHours": ["Mo-Fr 08:00-21:00", "Sa 09:00-18:00"],
        "geo": {
            "@type": "GeoCoordinates",
            "latitude": "50.515643",
            "longitude": "30.255479",
        },
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "вул. Стельмаха, 9а",
            "addressLocality": "Ірпінь",
            "addressCountry": "UA",
            "addressRegion": "Київська обл",
            "postalCode": "08200",
        },
    }
