"""Мапінг slug StaticPage → page_slug у PageSection для підказок в адмінці."""

SECTION_PAGE_SLUGS: dict[str, str] = {
    "about": "about",
    "contacts": "contacts",
    "home": "home",
    "blog": "blog",
    "reviews": "reviews",
    "neobhidni-dokumenty": "neobhidni-dokumenty",
    "kyiv-oblast": "kyiv-oblast",
    "tehnichni-pasporty-bti": "tehnichni-pasporty-bti",
    "bti-cina": "bti-cina",
    "vvedennya-v-ekspluatatsiyu": "vvedennya-v-ekspluatatsiyu",
    "legalizatsiya-neruhomosti": "legalizatsiya-neruhomosti",
    "dozvilna-dokumentatsiya": "dozvilna-dokumentatsiya",
    "zemelna-dokumentatsiya": "zemelna-dokumentatsiya",
    "dovidky": "dovidky",
    "poslugy-kyiv": "poslugy-kyiv",
    "tehnichnyj-pasport-na-kvartyru": "tehnichnyj-pasport-na-kvartyru",
    "tehnichnyj-pasport-na-budynok": "tehnichnyj-pasport-na-budynok",
    "elektronnyj-tehnichnyj-pasport": "elektronnyj-tehnichnyj-pasport",
    "tehnichnyj-pasport-na-budivlyu": "tehnichnyj-pasport-na-budivlyu",
    "tehnichnyj-pasport-na-garazh": "tehnichnyj-pasport-na-garazh",
    "tehnichnyj-pasport-na-nezhytlove-prymischennya": "tehnichnyj-pasport-na-nezhytlove-prymischennya",
    "tehnichnyj-pasport-na-bagato-kvartyrnyj-budynok": "tehnichnyj-pasport-na-bagato-kvartyrnyj-budynok",
    "tehnichna-inventaryzatsiya": "tehnichna-inventaryzatsiya",
    "kadastrovyj-nomer": "kadastrovyj-nomer",
    "vytiah-dzk": "vytiah-dzk",
    "vysnovky-bti": "vysnovky-bti",
}


def section_page_slug_for(static_slug: str) -> str | None:
    return SECTION_PAGE_SLUGS.get(static_slug)
