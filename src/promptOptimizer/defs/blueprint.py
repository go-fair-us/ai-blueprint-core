"""Fetch the NIAID Blueprint spec and slice out the API/metadata/PID guidance.

The full spec is long; we cache it once (under the configured outputdir) and
extract only the sections relevant to API structure, so the scoring judge is
grounded without paying for the whole document on every call.

Disk locations are controlled by ``defs.paths`` (``--workdir`` / ``--inputdir``
/ ``--outputdir``).
"""
from __future__ import annotations

import re
import urllib.request
from pathlib import Path

from defs import paths as pathconf

BLUEPRINT_URL = (
    "https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/"
    "refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md"
)

# Package root (for docs / defaults). Prefer pathconf for run I/O.
BASE = Path(__file__).resolve().parent.parent

# Backward-compatible aliases — track the configured output directory.
# Prefer importing helpers from defs.paths in new code.
def __getattr__(name: str):
    if name == "ARTIFACTS":
        return pathconf.OUTPUTDIR
    if name == "CACHE":
        return pathconf.blueprint_write_path()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# Sections whose heading mentions any of these are kept for the judge context.
_KEEP = (
    "api", "machine", "json-ld", "jsonld", "openapi", "swagger", "endpoint",
    "persistent identifier", "identifier", "doi", "orcid", "ror", "rrid",
    "metadata", "schema.org", "table 1", "interoper", "access", "citation",
)

_context_cache: str | None = None


def fetch_blueprint(refresh: bool = False) -> str:
    """Load Blueprint markdown from input/output dirs, or download and cache it."""
    if not refresh:
        existing = pathconf.blueprint_read_path()
        if existing is not None:
            return existing.read_text(encoding="utf-8")

    with urllib.request.urlopen(BLUEPRINT_URL, timeout=30) as resp:  # noqa: S310 (trusted URL)
        text = resp.read().decode("utf-8")
    cache = pathconf.blueprint_write_path()
    cache.write_text(text, encoding="utf-8")
    return text


def _split_sections(md: str) -> list[tuple[str, str]]:
    """Split markdown into (heading, body) pairs on ATX (``#``) headings."""
    sections: list[tuple[str, str]] = []
    heading = "(preamble)"
    buf: list[str] = []
    for line in md.splitlines():
        if re.match(r"^#{1,6}\s", line):
            if buf:
                sections.append((heading, "\n".join(buf)))
            heading = line.lstrip("#").strip()
            buf = [line]
        else:
            buf.append(line)
    if buf:
        sections.append((heading, "\n".join(buf)))
    return sections


def extract_api_context(md: str) -> str:
    """Keep only Blueprint sections relevant to APIs / metadata / identifiers."""
    keep = [
        body
        for heading, body in _split_sections(md)
        if any(k in heading.lower() for k in _KEEP) or "table 1" in body.lower()
    ]
    context = "\n\n".join(keep).strip()
    # Fallback: if slicing found nothing, use a truncated whole doc.
    return context or md[:12_000]


def get_blueprint_context(refresh: bool = False) -> str:
    """Cached, sliced Blueprint guidance (API/metadata/PID/citation sections)
    used to ground the scoring judge across every task."""
    global _context_cache
    if _context_cache is None or refresh:
        _context_cache = extract_api_context(fetch_blueprint(refresh=refresh))
    return _context_cache
