from django.contrib.sitemaps import Sitemap

from src.blog.models import BlogPost
from src.pages.models import StaticPage
from src.seo.models import SeoMetadata


class PublishedFilterMixin:
    def exclude_noindex(self, queryset, model_name: str):
        noindex_ids = SeoMetadata.objects.filter(
            content_type__model=model_name,
            robots_noindex=True,
        ).values_list("object_id", flat=True)
        return queryset.exclude(pk__in=noindex_ids)


class StaticPageSitemap(PublishedFilterMixin, Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        qs = StaticPage.objects.filter(is_published=True)
        return self.exclude_noindex(qs, "staticpage")

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


class BlogPostSitemap(PublishedFilterMixin, Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        qs = BlogPost.objects.filter(is_published=True)
        return self.exclude_noindex(qs, "blogpost")

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()
