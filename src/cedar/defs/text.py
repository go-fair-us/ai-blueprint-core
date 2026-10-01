"""Normalize LM literals before grounding and serialize."""
from __future__ import annotations

import re
from urllib.parse import urlparse

_PLACEHOLDERS = frozenset({"", "none", "null", "n/a", "na", "nil", "undefined"})
_YEAR_MONTH = re.compile(r"^(\d{4})-(\d{2})$")
_YEAR_MONTH_DAY = re.compile(r"^(\d{4})-(\d{2})-(\d{2})")
_BROKEN_MONTH_DT = re.compile(r"^(\d{4})-(\d{2})T")


def clean_literal(value: object | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    while len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'":
        text = text[1:-1].strip()
    if text.lower() in _PLACEHOLDERS:
        return None
    return text or None


def clean_iri(value: object | None) -> str | None:
    text = clean_literal(value)
    if not text:
        return None
    if " " in text and not text.startswith("http"):
        return None
    return text


def normalize_temporal(value: object | None) -> str | None:
    """Return a value safe for xsd:dateTime (or None).

    Month-only ``YYYY-MM`` becomes ``YYYY-MM-01T00:00:00``.
    Rejects ``YYYY-MMT00:00:00``.
    """
    text = clean_literal(value)
    if not text:
        return None
    broken = _BROKEN_MONTH_DT.match(text)
    if broken:
        text = f"{broken.group(1)}-{broken.group(2)}"
    if "T" in text:
        date_part, _, rest = text.partition("T")
        if _YEAR_MONTH.fullmatch(date_part) and not _YEAR_MONTH_DAY.match(date_part):
            text = date_part
        elif _YEAR_MONTH_DAY.match(date_part):
            return f"{date_part[:10]}T{rest}" if rest else f"{date_part[:10]}T00:00:00"
    ym = _YEAR_MONTH.fullmatch(text)
    if ym:
        return f"{ym.group(1)}-{ym.group(2)}-01T00:00:00"
    ymd = _YEAR_MONTH_DAY.match(text)
    if ymd:
        if "T" in text:
            return text
        return f"{text[:10]}T00:00:00"
    return text


def url_path(value: str) -> str | None:
    parsed = urlparse(value.strip())
    path = parsed.path or ""
    return path if len(path) > 3 else None
