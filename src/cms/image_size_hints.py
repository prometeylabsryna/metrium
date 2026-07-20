"""Рекомендовані розміри зображень для адмінки (орієнтир по поточних ассетах сайту)."""

from __future__ import annotations

# Базові підказки (px). Формат WebP/JPEG, без прозорості для фото.
HINT_HERO_DESKTOP = (
    "Рекомендовано: 1920×1080 px або більше (альбомна орієнтація). "
    "Оптимально як на сайті: ~2560×1680. Формат WebP/JPEG, до 1–1.5 МБ."
)
HINT_HERO_MOBILE = (
    "Рекомендовано: 400×520 px (портрет ~3:4), як мобільний банер на сайті. "
    "Формат WebP/JPEG, до 300 КБ."
)
HINT_DOC_EXAMPLE = (
    "Рекомендовано: 1200×1700 px або більше (портрет, як зразок документа). "
    "Оптимально ~1650×2400. Формат WebP/JPEG, чіткий скан/фото."
)
HINT_GALLERY = (
    "Рекомендовано: 1024×683 px (альбом ~3:2). Формат WebP/JPEG, до 400 КБ."
)
HINT_BADGE = (
    "Рекомендовано: 380×380 px (квадрат). PNG/WebP з прозорістю за потреби."
)
HINT_ICON = (
    "Рекомендовано: 128×128 px (квадратна іконка), PNG/WebP. "
    "Можна 64×64 для дрібних іконок."
)
HINT_LOGO = (
    "Рекомендовано: ширина 200–320 px, висота до 80 px (горизонтальний логотип). PNG/WebP."
)
HINT_ABOUT_PHOTO = (
    "Рекомендовано: 1200×540 px або ~732×330 (широке фото секції). WebP/JPEG."
)
HINT_BLOG = (
    "Рекомендовано: 1200×630 px (обкладинка поста, ~1.91:1). WebP/JPEG, до 500 КБ."
)
HINT_SECTION = (
    "Рекомендовано: 1200×800 px (альбом) або квадрат 800×800 — залежно від місця на сторінці. WebP/JPEG."
)
HINT_BLOCK = (
    "Рекомендовано: 1200×800 px для банерів у блоках. WebP/JPEG."
)
HINT_DESKTOP_DEFAULT = (
    "Рекомендовано: 1920×1080 px (десктоп). Формат WebP/JPEG."
)
HINT_MOBILE_DEFAULT = (
    "Рекомендовано: 800×1000 px (мобільне). Формат WebP/JPEG."
)


def hint_for_site_image(image_key: str = "", *, mobile: bool = False) -> str:
    """Підказка для SiteImage за image_key."""
    key = (image_key or "").lower()
    if mobile:
        if key == "hero" or key.startswith("hero"):
            return HINT_HERO_MOBILE
        return HINT_MOBILE_DEFAULT

    if key == "hero" or key.startswith("hero"):
        return HINT_HERO_DESKTOP
    if key in ("doc.example", "doc_example") or key.startswith("doc."):
        return HINT_DOC_EXAMPLE
    if key.startswith("gallery.") or "marquee" in key:
        return HINT_GALLERY
    if "badge" in key or key.endswith(".badge"):
        return HINT_BADGE
    if "garant" in key or key.startswith("qual."):
        return HINT_BADGE
    if key in ("why.photo", "about.passport", "bg.page"):
        return HINT_ABOUT_PHOTO
    if key.startswith("static."):
        return HINT_SECTION
    return HINT_DESKTOP_DEFAULT


def apply_site_image_hints(form, *, image_key: str = "") -> None:
    """Проставляє help_text на поля image / image_mobile форми SiteImage."""
    if "image" in form.fields:
        form.fields["image"].help_text = hint_for_site_image(image_key, mobile=False)
    if "image_mobile" in form.fields:
        form.fields["image_mobile"].help_text = hint_for_site_image(image_key, mobile=True)
