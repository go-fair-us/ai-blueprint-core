"""Load and section-slice Blueprint + Work Plans for the LLM judge."""
from __future__ import annotations

import re
from pathlib import Path

from defs import paths as pathconf

_DEFAULT_KEEP = (
    "metadata",
    "schema.org",
    "table 1",
    "identifier",
    "doi",
    "orcid",
    "ror",
    "rrid",
    "persistent identifier",
    "pid",
    "api",
    "machine",
    "openapi",
    "swagger",
    "json-ld",
    "jsonld",
    "citation",
    "outreach",
    "training",
    "fair",
    "work plan",
    "repository",
    "digital object",
    "access",
    "license",
    "funder",
    "author",
    "infectious",
    "host",
    "health condition",
    "interoper",
    "endpoint",
    "discovery",
    "portal",
)

_context_cache: str | None = None


def _split_sections(md: str) -> list[tuple[str, str]]:
    """Split markdown into (heading, body) pairs on ATX headings."""
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


def slice_by_keywords(
    md: str,
    keep_keywords: list[str] | tuple[str, ...] | None = None,
    *,
    fallback_chars: int = 8_000,
) -> str:
    """Keep sections whose heading or body matches any keep keyword."""
    keys = tuple(k.lower() for k in (keep_keywords or _DEFAULT_KEEP))
    keep = []
    for heading, body in _split_sections(md):
        h = heading.lower()
        b = body.lower()
        if any(k in h or k in b for k in keys):
            keep.append(body)
    context = "\n\n".join(keep).strip()
    return context or md[:fallback_chars]


def _cap(text: str, max_chars: int) -> str:
    if max_chars <= 0 or len(text) <= max_chars:
        return text
    # Prefer cutting at a paragraph boundary near the limit.
    cut = text[:max_chars]
    last_break = cut.rfind("\n\n")
    if last_break > max_chars // 2:
        cut = cut[:last_break]
    return cut.rstrip() + "\n\n… [truncated for judge context budget]"


def load_markdown(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(f"Guidance document not found: {path}")
    return path.read_text(encoding="utf-8")


def build_guidance_context(
    *,
    blueprint_path: Path,
    workplans_path: Path,
    keep_keywords: list[str] | None = None,
    max_chars: int = 14_000,
    refresh: bool = False,
    cache: bool = True,
) -> str:
    """Build combined, sliced Blueprint + Work Plans context for the judge."""
    global _context_cache
    if _context_cache is not None and not refresh:
        return _context_cache

    if not refresh:
        cached = pathconf.OUTPUTDIR / "guidance.md"
        if cache and cached.is_file() and cached.stat().st_size > 0:
            _context_cache = cached.read_text(encoding="utf-8")
            return _context_cache

    bp = load_markdown(blueprint_path)
    wp = load_markdown(workplans_path)
    keys = keep_keywords or list(_DEFAULT_KEEP)

    bp_slice = slice_by_keywords(bp, keys)
    wp_slice = slice_by_keywords(wp, keys)

    # Split budget roughly 60/40 Blueprint / Work Plans.
    bp_budget = int(max_chars * 0.6)
    wp_budget = max_chars - bp_budget
    combined = (
        "## Blueprint (sliced)\n\n"
        + _cap(bp_slice, bp_budget)
        + "\n\n## Work Plans Supplementary (sliced)\n\n"
        + _cap(wp_slice, wp_budget)
    )

    if cache:
        out = pathconf.guidance_write_path()
        out.write_text(combined, encoding="utf-8")

    _context_cache = combined
    return combined


def get_guidance_context(
    *,
    blueprint_path: Path | None = None,
    workplans_path: Path | None = None,
    keep_keywords: list[str] | None = None,
    max_chars: int = 14_000,
    refresh: bool = False,
) -> str:
    """Cached guidance context; paths required on first call if cache empty."""
    global _context_cache
    if _context_cache is not None and not refresh:
        return _context_cache
    if blueprint_path is None or workplans_path is None:
        raise RuntimeError(
            "guidance not initialized: call build_guidance_context with paths first"
        )
    return build_guidance_context(
        blueprint_path=blueprint_path,
        workplans_path=workplans_path,
        keep_keywords=keep_keywords,
        max_chars=max_chars,
        refresh=refresh,
    )


def clear_guidance_cache() -> None:
    global _context_cache
    _context_cache = None
