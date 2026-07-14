from django.db.models import Case, F, FloatField, Value, When
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.views import View

from src.blog.models import BlogPost
from src.cms.models import PageBlock
from src.core.models import Office
from src.i18n.models import Language
from src.pages.models import StaticPage
from src.pages.ru_prefix import legacy_ru_prefixed_slug
from src.reviews.models import Review
from src.seo.services import get_seo_for_object


class PageDetailView(View):
    language = Language.UA

    def get(self, request, slug=""):
        if slug == "":
            page = StaticPage.objects.filter(
                language=self.language,
                is_published=True,
                is_home=True,
            ).first()
            if not page:
                page = StaticPage.objects.filter(
                    language=self.language,
                    is_published=True,
                    slug__in=["home", "golovna", "golovna-2", ""],
                ).first()
        else:
            page = StaticPage.objects.filter(
                slug=slug,
                language=self.language,
                is_published=True,
            ).first()
            # Legacy WP: RU pages stored as slug "ru-{slug}" with language=ua
            if not page and self.language == Language.RU:
                page = StaticPage.objects.filter(
                    slug=legacy_ru_prefixed_slug(slug),
                    is_published=True,
                ).first()
            # Fallback: allow standard slugs to render even without a DB page
            if not page:
                service_slugs = (
                    "about", "contacts", "blog", "reviews",
                    "kyiv-oblast",
                    "tehnichni-pasporty-bti", "bti-cina",
                    "vvedennya-v-ekspluatatsiyu",
                    "legalizatsiya-neruhomosti", "dozvilna-dokumentatsiya",
                    "zemelna-dokumentatsiya", "dovidky",
                    "poslugy-kyiv", "neobhidni-dokumenty",
                    "tehnichnyj-pasport-na-kvartyru",
                    "tehnichnyj-pasport-na-budynok",
                    "elektronnyj-tehnichnyj-pasport",
                    "tehnichnyj-pasport-na-budivlyu",
                    "tehnichnyj-pasport-na-garazh",
                    "tehnichnyj-pasport-na-nezhytlove-prymischennya",
                    "tehnichnyj-pasport-na-bagato-kvartyrnyj-budynok",
                    "tehnichna-inventaryzatsiya",
                    "kadastrovyj-nomer",
                    "vytiah-dzk",
                    "vysnovky-bti",
                )
                if slug not in service_slugs:
                    raise Http404()

        seo = get_seo_for_object(page) if page else None

        # Blog list — усі статті на одній сторінці, як на metrium.com.ua/blog/
        if slug == "blog" or (page and page.slug == "blog"):
            posts = BlogPost.objects.filter(
                language=self.language,
                is_published=True,
            ).order_by("-published_at")
            return render(
                request,
                "blog/list.html",
                {"page": page, "posts": posts, "seo": seo, "page_slug": "blog"},
            )

        # About page
        if slug == "about" or (page and (page.template_key == "template-about.php" or page.slug == "about")):
            return render(
                request,
                "pages/about.html",
                {"page": page, "seo": seo, "page_slug": "about"},
            )

        # Contacts page
        if slug == "contacts" or (page and page.slug == "contacts"):
            offices = (
                Office.objects.filter(is_active=True)
                .annotate(
                    live_sort=Case(
                        When(is_main=True, then=Value(7.5)),
                        default=F("sort_order"),
                        output_field=FloatField(),
                    )
                )
                .order_by("live_sort", "id")
            )
            return render(
                request,
                "pages/contacts.html",
                {"page": page, "offices": offices, "seo": seo, "page_slug": "contacts"},
            )

        # Service pages with dedicated templates
        SERVICE_TEMPLATES = {
            "kyiv-oblast": "pages/services/kyiv_oblast.html",
            "tehnichni-pasporty-bti": "pages/services/tehnichni_pasporty.html",
            "bti-cina": "pages/services/bti_cina.html",
            "vvedennya-v-ekspluatatsiyu": "pages/services/vvedennya.html",
            "legalizatsiya-neruhomosti": "pages/services/legalizatsiya.html",
            "dozvilna-dokumentatsiya": "pages/services/dozvilna.html",
            "zemelna-dokumentatsiya": "pages/services/zemelna.html",
            "dovidky": "pages/services/dovidky.html",
            "poslugy-kyiv": "pages/services/poslugy.html",
            "neobhidni-dokumenty": "pages/neobhidni_dokumenty.html",
            "tehnichnyj-pasport-na-kvartyru": "pages/services/pasport_kvartyra.html",
            "tehnichnyj-pasport-na-budynok": "pages/services/pasport_budynok.html",
            "elektronnyj-tehnichnyj-pasport": "pages/services/pasport_elektronnyj.html",
            "tehnichnyj-pasport-na-budivlyu": "pages/services/pasport_budivlya.html",
            "tehnichnyj-pasport-na-garazh": "pages/services/pasport_garazh.html",
            "tehnichnyj-pasport-na-nezhytlove-prymischennya": "pages/services/pasport_nezhytlove.html",
            "tehnichnyj-pasport-na-bagato-kvartyrnyj-budynok": "pages/services/pasport_mbd.html",
            "tehnichna-inventaryzatsiya": "pages/services/inventaryzatsiya.html",
            "kadastrovyj-nomer": "pages/services/kadastrovyj_nomer.html",
            "vytiah-dzk": "pages/services/vytiah_dzk.html",
            "vysnovky-bti": "pages/services/vysnovky_bti.html",
        }
        effective_slug = page.slug if page else slug
        if effective_slug in SERVICE_TEMPLATES:
            return render(
                request,
                SERVICE_TEMPLATES[effective_slug],
                {"page": page, "seo": seo, "page_slug": effective_slug},
            )

        # Home page
        if not page or page.is_home or page.slug in ("home", "golovna", "golovna-2", ""):
            featured_reviews = Review.objects.filter(
                is_published=True, is_featured=True
            ).order_by("-published_at")[:6]
            offices = Office.objects.filter(is_active=True).order_by("sort_order")
            return render(
                request,
                "pages/home.html",
                {
                    "page": page,
                    "featured_reviews": featured_reviews,
                    "offices": offices,
                    "seo": seo,
                    "page_slug": "home",
                },
            )

        # Generic block builder
        blocks = PageBlock.objects.filter(
            content_type__model="staticpage",
            object_id=page.pk,
            is_visible=True,
        )
        return render(
            request,
            "pages/constructor.html",
            {
                "page": page,
                "blocks": blocks,
                "seo": seo,
                "page_slug": page.slug,
            },
        )


class PageDetailViewRu(PageDetailView):
    language = Language.RU


REGION_SLUGS = {
    "kyiv-oblast": {
        "bila-tserkva": "Біла Церква",
        "brovary": "Бровари",
        "irpin": "Ірпінь",
        "boryspil": "Бориспіль",
        "vyshhorod": "Вишгород",
        "vasylkiv": "Васильків",
        "vyshneve": "Вишневе",
        "obukhiv": "Обухів",
        "fastiv": "Фастів",
        "bucha": "Буча",
        "boyarka": "Боярка",
        "borodyanka": "Бородянка",
        "makariv": "Макарів",
        "koziatyn": "Козятин",
        "hostomel": "Гостомель",
        "sofiivska-borschahivka": "Софіївська Борщагівка",
        "baryshivka": "Баришівка",
    }
}

REGION_NAMES_RU = {
    "bila-tserkva": "Белая Церковь",
    "brovary": "Бровары",
    "irpin": "Ирпень",
    "boryspil": "Борисполь",
    "vyshhorod": "Вышгород",
    "vasylkiv": "Васильков",
    "vyshneve": "Вишнёвое",
    "obukhiv": "Обухов",
    "fastiv": "Фастов",
    "bucha": "Буча",
    "boyarka": "Боярка",
    "borodyanka": "Бородянка",
    "makariv": "Макаров",
    "koziatyn": "Казатин",
    "hostomel": "Гостомель",
    "sofiivska-borschahivka": "Софиевская Борщаговка",
    "baryshivka": "Барышевка",
}


class RegionPageView(View):
    language = Language.UA

    def get(self, request, parent, city):
        cities = REGION_SLUGS.get(parent)
        if not cities or city not in cities:
            raise Http404()

        city_name_ua = cities[city]
        city_name_ru = REGION_NAMES_RU.get(city, city_name_ua)
        city_name = city_name_ua if self.language == Language.UA else city_name_ru

        full_slug = f"{parent}/{city}"
        page = StaticPage.objects.filter(
            slug=full_slug,
            language=self.language,
            is_published=True,
        ).first()

        seo = get_seo_for_object(page) if page else None
        return render(
            request,
            "pages/services/bti_region.html",
            {
                "page": page,
                "seo": seo,
                "city_name": city_name,
                "city_slug": city,
                "parent_slug": parent,
                "language": self.language,
                "page_slug": parent,
            },
        )


class RegionPageViewRu(RegionPageView):
    language = Language.RU
