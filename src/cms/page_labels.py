"""Людські назви сторінок і посилання для адмінки."""

from src.cms.models import PageSection

PAGE_PUBLIC_URLS: dict[str, str] = {
    "global": "/",
    "header": "/",
    "footer": "/",
    "home": "/",
    "about": "/about/",
    "contacts": "/contacts/",
    "blog": "/blog/",
    "reviews": "/reviews/",
    "neobhidni-dokumenty": "/neobhidni-dokumenty/",
    "kyiv-oblast": "/kyiv-oblast/",
    "tehnichni-pasporty-bti": "/tehnichni-pasporty-bti/",
    "bti-cina": "/bti-cina/",
    "vvedennya-v-ekspluatatsiyu": "/vvedennya-v-ekspluatatsiyu/",
    "legalizatsiya-neruhomosti": "/legalizatsiya-neruhomosti/",
    "dozvilna-dokumentatsiya": "/dozvilna-dokumentatsiya/",
    "zemelna-dokumentatsiya": "/zemelna-dokumentatsiya/",
    "dovidky": "/dovidky/",
    "poslugy-kyiv": "/poslugy-kyiv/",
    "tehnichnyj-pasport-na-kvartyru": "/tehnichnyj-pasport-na-kvartyru/",
    "tehnichnyj-pasport-na-budynok": "/tehnichnyj-pasport-na-budynok/",
    "elektronnyj-tehnichnyj-pasport": "/elektronnyj-tehnichnyj-pasport/",
    "tehnichnyj-pasport-na-budivlyu": "/tehnichnyj-pasport-na-budivlyu/",
    "tehnichnyj-pasport-na-garazh": "/tehnichnyj-pasport-na-garazh/",
    "tehnichnyj-pasport-na-nezhytlove-prymischennya": "/tehnichnyj-pasport-na-nezhytlove-prymischennya/",
    "tehnichnyj-pasport-na-bagato-kvartyrnyj-budynok": "/tehnichnyj-pasport-na-bagato-kvartyrnyj-budynok/",
    "tehnichna-inventaryzatsiya": "/tehnichna-inventaryzatsiya/",
    "kadastrovyj-nomer": "/kadastrovyj-nomer/",
    "vytiah-dzk": "/vytiah-dzk/",
    "vysnovky-bti": "/vysnovky-bti/",
}


def page_label(page_slug: str) -> str:
    choices = dict(PageSection.PAGE_CHOICES)
    return choices.get(page_slug, page_slug)


def page_public_url(page_slug: str) -> str:
    return PAGE_PUBLIC_URLS.get(page_slug, "/")


def admin_sections_url(page_slug: str) -> str:
    return f"/admin/cms/pagesection/?page_slug__exact={page_slug}"
