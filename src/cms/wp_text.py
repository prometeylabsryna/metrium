"""Sanitize WordPress import artifacts in HTML/text bodies."""

from __future__ import annotations

import re


def sanitize_wp_newlines(body: str) -> str:
    """Fix WP import artefacts where ``\\r\\n`` became literal ``rn``."""
    if not body:
        return ""
    text = body.replace("</br>", "")
    text = text.replace("<br></br>", "<br />")
    text = text.replace("rnrn", "<br /><br />")
    text = re.sub(r"rn(?=[<\t])", "", text)
    text = re.sub(r"rn(?=[А-ЯІЇЄҐA-Zа-яіїєґ])", "<br />", text)
    text = re.sub(r"(?<=[А-ЯІЇЄҐA-Zа-яіїєґ.?!:;])rn(?=\s)", "<br />", text)
    text = re.sub(r"rn", " ", text)
    return text.strip()
