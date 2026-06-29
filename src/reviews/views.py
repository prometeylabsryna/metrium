from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404, render
from django.views import View

from src.i18n.models import Language
from src.pages.models import StaticPage
from src.reviews.models import Review
from src.seo.services import get_seo_for_object


class ReviewsView(View):
    language = Language.UA

    def get(self, request):
        reviews = Review.objects.filter(is_published=True)
        agg = reviews.aggregate(avg=Avg("rating"), total=Count("id"))
        rating_avg = round(agg["avg"] or 0, 1)
        rating_count = agg["total"]

        distribution = {}
        for star in range(5, 0, -1):
            cnt = reviews.filter(rating=star).count()
            pct = round(cnt / rating_count * 100) if rating_count else 0
            distribution[star] = {"count": cnt, "pct": pct}

        page = StaticPage.objects.filter(
            slug="reviews",
            language=self.language,
            is_published=True,
        ).first()
        seo = get_seo_for_object(page) if page else None

        return render(
            request,
            "reviews/list.html",
            {
                "reviews": reviews,
                "rating_avg": rating_avg,
                "rating_count": rating_count,
                "rating_distribution": distribution,
                "page": page,
                "seo": seo,
            },
        )


class ReviewsViewRu(ReviewsView):
    language = Language.RU
