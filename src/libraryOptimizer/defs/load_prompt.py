"""Load OKF prompt examples: strip YAML front matter, extract # Prompt body."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

# Optional simple front-matter key parsing (no full YAML dependency for tags).
_FM_TITLE = re.compile(r"^title:\s*(.+)$", re.MULTILINE)
_FM_TAGS = re.compile(r"^tags:\s*\[([^\]]*)\]", re.MULTILINE)
_PROMPT_HEADING = re.compile(r"^#\s+Prompt\s*$", re.MULTILINE | re.IGNORECASE)


@dataclass(frozen=True)
class LibraryPrompt:
    """One OKF prompt example ready to use as GEPA seed instructions."""

    path: Path
    slug: str
    body: str
    title: str = ""
    tags: list[str] = field(default_factory=list)
    front_matter: str = ""


def strip_front_matter(text: str) -> tuple[str, str]:
    """Return ``(front_matter_raw, body)``. Empty front matter if none."""
    if not text.startswith("---"):
        return "", text
    # Find closing --- on its own line after the opening.
    rest = text[3:]
    # Allow optional newline after opening ---
    if rest.startswith("\r\n"):
        rest = rest[2:]
    elif rest.startswith("\n"):
        rest = rest[1:]
    else:
        return "", text

    for match in re.finditer(r"(?m)^---\s*$", rest):
        fm = rest[: match.start()].strip("\n")
        body = rest[match.end() :].lstrip("\n")
        return fm, body
    return "", text


def extract_prompt_body(body: str) -> str:
    """Prefer content under ``# Prompt``; otherwise return full body stripped."""
    m = _PROMPT_HEADING.search(body)
    if not m:
        return body.strip()
    after = body[m.end() :]
    # Stop at next top-level ATX heading if present
    next_h = re.search(r"(?m)^#\s+\S", after)
    if next_h:
        after = after[: next_h.start()]
    return after.strip()


def parse_front_matter_meta(fm: str) -> tuple[str, list[str]]:
    """Pull title and tags from front matter without a YAML parser."""
    title = ""
    tags: list[str] = []
    tm = _FM_TITLE.search(fm)
    if tm:
        title = tm.group(1).strip().strip("\"'")
    gm = _FM_TAGS.search(fm)
    if gm:
        raw = gm.group(1)
        tags = [t.strip().strip("\"'") for t in raw.split(",") if t.strip()]
    return title, tags


def slug_from_path(path: Path, examples_root: Path | None = None) -> str:
    """Stable slug: path under examples_root with ``/`` → ``-``, else stem."""
    path = path.resolve()
    if examples_root is not None:
        try:
            rel = path.relative_to(examples_root.resolve())
            parts = list(rel.with_suffix("").parts)
            if parts:
                return "-".join(parts)
        except ValueError:
            pass
    # Try to find prompt_examples in parents
    for parent in path.parents:
        if parent.name == "prompt_examples":
            try:
                rel = path.relative_to(parent)
                return "-".join(rel.with_suffix("").parts)
            except ValueError:
                break
    return path.stem


def load_library_prompt(
    path: str | Path,
    *,
    examples_root: Path | None = None,
) -> LibraryPrompt:
    """Load a prompt example file into a LibraryPrompt."""
    p = Path(path).expanduser().resolve()
    if not p.is_file():
        raise FileNotFoundError(f"Prompt file not found: {p}")
    text = p.read_text(encoding="utf-8")
    fm, after_fm = strip_front_matter(text)
    body = extract_prompt_body(after_fm)
    if not body:
        raise ValueError(f"No prompt body found in {p}")
    title, tags = parse_front_matter_meta(fm)
    slug = slug_from_path(p, examples_root)
    return LibraryPrompt(
        path=p,
        slug=slug,
        body=body,
        title=title or p.stem,
        tags=tags,
        front_matter=fm,
    )


def list_prompt_files(examples_root: Path) -> list[Path]:
    """All ``*.md`` leaves under examples_root except README."""
    root = examples_root.resolve()
    if not root.is_dir():
        return []
    files = sorted(
        p
        for p in root.rglob("*.md")
        if p.is_file() and p.name.lower() != "readme.md"
    )
    return files
