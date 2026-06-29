from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import index as sitemap_index
from django.contrib.sitemaps.views import sitemap as sitemap_view
from django.urls import include, path

from src.blog.views import BlogDetailView, BlogDetailViewRu
from src.core.views import HealthView, RobotsView
from src.leads.views import CalculatorLeadView, PhoneLeadView, ReviewLeadView
from src.pages.views import PageDetailView, PageDetailViewRu, RegionPageView, RegionPageViewRu
from src.reviews.views import ReviewsView, ReviewsViewRu
from src.seo.sitemaps import BlogPostSitemap, StaticPageSitemap

sitemaps = {
    "pages": StaticPageSitemap,
    "blog": BlogPostSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("tinymce/", include("tinymce.urls")),
    path("healthz/", HealthView.as_view(), name="healthz"),
    path("robots.txt", RobotsView.as_view(), name="robots"),
    path(
        "sitemap.xml",
        sitemap_index,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.index",
    ),
    path(
        "sitemap-<section>.xml",
        sitemap_view,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("api/leads/phone/", PhoneLeadView.as_view(), name="leads-phone"),
    path("api/leads/calculator/", CalculatorLeadView.as_view(), name="leads-calculator"),
    path("api/leads/review/", ReviewLeadView.as_view(), name="leads-review"),
    path("ru/blogs/<slug>/", BlogDetailViewRu.as_view(), name="blog-detail-ru"),
    path("blogs/<slug>/", BlogDetailView.as_view(), name="blog-detail"),
    path("reviews/", ReviewsView.as_view(), name="reviews"),
    path("ru/reviews/", ReviewsViewRu.as_view(), name="reviews-ru"),
    path("ru/", PageDetailViewRu.as_view(), name="home-ru"),
    path("ru/<slug:parent>/<slug:city>/", RegionPageViewRu.as_view(), name="region-detail-ru"),
    path("ru/<slug>/", PageDetailViewRu.as_view(), name="page-detail-ru"),
    path("", PageDetailView.as_view(), name="home"),
    path("<slug:parent>/<slug:city>/", RegionPageView.as_view(), name="region-detail"),
    path("<slug>/", PageDetailView.as_view(), name="page-detail"),
]

if settings.DEBUG or getattr(settings, "SERVE_USER_UPLOADS", False):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(
        "/wp-content/uploads/",
        document_root=settings.WP_UPLOADS_ROOT,
    )
