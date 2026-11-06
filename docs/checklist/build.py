#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "markdown==3.11",
#   "weasyprint==70.0",
# ]
# ///
"""Render checklist.md to filtered HTML and PDF views.

The Markdown file is the only content authority. This script parses
structured item headings, optionally keeps a subset of capability
levels, and prints HTML (for browsers) or PDF (for paper). It does
not invent checklist text.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path

import markdown
from weasyprint import CSS, HTML

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "checklist.md"
STYLE = HERE / "style.css"
DIST = HERE / "dist"

ITEM_RE = re.compile(r"^### ([A-Z]{2,4}-\d+)\. (.+)$")
SECTION_RE = re.compile(r"^## (.+)$")
FIELD_RE = re.compile(r"^- \*\*(.+?):\*\*\s*(.*)$")
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

REQUIRED_FIELDS = (
    "Level",
    "Pillar",
    "Optional",
    "Kind",
    "Maturity",
    "Access needed",
    "Maintenance",
    "Sources",
)

MD_EXTENSIONS = ["extra", "sane_lists"]
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass(frozen=True)
class Revision:
    """Stable identity of the checklist *source*, not the clock at build time.

    ``date`` is a review/source date (git commit day of checklist.md, an
    explicit --date, or SOURCE_DATE_EPOCH). It is not today's build date
    and not an evidence date for cited standards or the webinar itself.
    """

    date: str
    version: str
    date_source: str


def _git(args: list[str]) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=HERE,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    return value or None


def source_version() -> str:
    sha = _git(["log", "-1", "--format=%h", "--", SOURCE.name])
    if sha:
        return sha
    digest = hashlib.sha256(SOURCE.read_bytes() if SOURCE.exists() else b"").hexdigest()
    return digest[:12]


def parse_iso_date(value: str) -> str:
    if not ISO_DATE_RE.match(value):
        raise ValueError(f"dates must be YYYY-MM-DD, not {value!r}")
    date.fromisoformat(value)  # raises for impossible calendar dates
    return value


def revision_date_from_front_matter(text: str) -> str | None:
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    for line in text[3:end].splitlines():
        if line.startswith("revision_date:"):
            value = line.split(":", 1)[1].strip().strip("'\"")
            return parse_iso_date(value) if ISO_DATE_RE.match(value) else None
    return None


def resolve_revision(cli_date: str | None = None, source_text: str | None = None) -> Revision:
    version = source_version()
    if cli_date:
        return Revision(parse_iso_date(cli_date), version, "cli")
    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    if epoch:
        try:
            derived = datetime.fromtimestamp(int(epoch), tz=timezone.utc).date().isoformat()
        except (TypeError, ValueError) as exc:
            raise ValueError(f"invalid SOURCE_DATE_EPOCH: {epoch!r}") from exc
        return Revision(derived, version, "source-date-epoch")
    text = source_text if source_text is not None else (
        SOURCE.read_text(encoding="utf-8") if SOURCE.exists() else ""
    )
    from_source = revision_date_from_front_matter(text)
    if from_source:
        return Revision(from_source, version, "front-matter")
    git_date = _git(["log", "-1", "--format=%cs", "--", SOURCE.name])
    if git_date and ISO_DATE_RE.match(git_date):
        return Revision(git_date, version, "git")
    return Revision("unknown", version, "unknown")


def relocate_html_urls(html_text: str, source_dir: Path, output_dir: Path) -> str:
    """Rewrite relative href/src so HTML written into dist/ still resolves."""

    def repl(match: re.Match[str]) -> str:
        attr, url = match.group(1), match.group(2)
        if url.startswith(("http://", "https://", "mailto:", "#", "data:")):
            return match.group(0)
        path_part, _, fragment = url.partition("#")
        if not path_part:
            return match.group(0)
        # Generated HTML and a copied style.css both live in dist/. Leave the
        # stylesheet href alone so standalone HTML keeps a sibling CSS file.
        if path_part == "style.css":
            return match.group(0)
        target = (source_dir / path_part).resolve()
        relocated = Path(os.path.relpath(target, output_dir)).as_posix()
        if fragment:
            relocated = f"{relocated}#{fragment}"
        return f'{attr}="{relocated}"'

    return re.sub(r'(href|src)="([^"]+)"', repl, html_text)


@dataclass
class Item:
    item_id: str
    title: str
    fields: dict[str, str]
    body: str

    @property
    def level(self) -> int:
        return int(self.fields["Level"])

    @property
    def optional(self) -> bool:
        return self.fields["Optional"].strip().lower() == "yes"

    @property
    def pillar(self) -> str:
        return self.fields["Pillar"]


@dataclass
class Section:
    title: str
    intro: str = ""
    items: list[Item] = field(default_factory=list)


@dataclass
class Document:
    preamble: str
    sections: list[Section]

    @property
    def items(self) -> list[Item]:
        return [item for section in self.sections for item in section.items]


def md_inline(text: str) -> str:
    """Render a field (which may contain links) as HTML without a wrapping block."""
    rendered = markdown.markdown(text.strip(), extensions=["extra"])
    rendered = re.sub(r"^<p>", "", rendered)
    rendered = re.sub(r"</p>\s*$", "", rendered)
    return rendered


def md_blocks(text: str) -> str:
    return markdown.markdown(text.strip(), extensions=MD_EXTENSIONS) if text.strip() else ""


def parse_item(heading_id: str, heading_title: str, raw: str) -> Item:
    lines = raw.splitlines()
    fields: dict[str, str] = {}
    body_start = 0
    for index, line in enumerate(lines):
        if not line.strip():
            if fields:
                body_start = index + 1
                break
            continue
        match = FIELD_RE.match(line)
        if match:
            fields[match.group(1)] = match.group(2).strip()
            body_start = index + 1
            continue
        if fields:
            body_start = index
            break
    missing = [name for name in REQUIRED_FIELDS if name not in fields]
    if missing:
        raise ValueError(f"{heading_id} is missing fields: {', '.join(missing)}")
    try:
        level = int(fields["Level"])
    except ValueError as exc:
        raise ValueError(f"{heading_id} has a non-integer Level: {fields['Level']!r}") from exc
    if level not in (1, 2, 3):
        raise ValueError(f"{heading_id} Level must be 1, 2, or 3, not {level}")
    optional = fields["Optional"].strip().lower()
    if optional not in {"yes", "no"}:
        raise ValueError(f"{heading_id} Optional must be yes or no, not {fields['Optional']!r}")
    return Item(
        item_id=heading_id,
        title=heading_title,
        fields=fields,
        body="\n".join(lines[body_start:]).strip(),
    )


def strip_front_matter(text: str) -> str:
    if not text.startswith("---"):
        return text
    end = text.find("\n---", 3)
    if end == -1:
        return text
    rest = text[end + 4:]
    return rest[1:] if rest.startswith("\n") else rest


def parse_document(text: str) -> Document:
    text = strip_front_matter(text)
    lines = text.splitlines()
    preamble: list[str] = []
    sections: list[Section] = []
    current: Section | None = None
    item_id: str | None = None
    item_title: str | None = None
    bucket: list[str] = []

    def flush_item() -> None:
        nonlocal item_id, item_title, bucket
        if item_id is None or current is None:
            return
        current.items.append(parse_item(item_id, item_title or "", "\n".join(bucket)))
        item_id = None
        item_title = None
        bucket = []

    def flush_intro_or_item() -> None:
        nonlocal bucket
        if current is None:
            bucket = []
            return
        if item_id is None:
            extra = "\n".join(bucket).strip()
            if extra:
                current.intro = f"{current.intro}\n\n{extra}".strip() if current.intro else extra
            bucket = []
            return
        flush_item()

    for line in lines:
        section_match = SECTION_RE.match(line)
        item_match = ITEM_RE.match(line)
        if item_match:
            if current is None:
                raise ValueError(f"Item {item_match.group(1)} appears before a section heading")
            flush_intro_or_item()
            item_id = item_match.group(1)
            item_title = item_match.group(2)
            continue
        if section_match:
            flush_intro_or_item()
            current = Section(title=section_match.group(1))
            sections.append(current)
            bucket = []
            continue
        if current is None:
            preamble.append(line)
        else:
            bucket.append(line)
    flush_intro_or_item()
    return Document(preamble="\n".join(preamble).strip(), sections=sections)


def filter_document(doc: Document, levels: set[int] | None) -> Document:
    if not levels:
        return doc
    sections = []
    for section in doc.sections:
        items = [item for item in section.items if item.level in levels]
        if section.items and not items:
            continue
        sections.append(Section(title=section.title, intro=section.intro, items=items))
    return Document(preamble=doc.preamble, sections=sections)


def split_body(body: str) -> dict[str, str]:
    parts = {"do": "", "verify": "", "watch": "", "other": ""}
    current = "other"
    collected: dict[str, list[str]] = {key: [] for key in parts}
    for line in body.splitlines():
        stripped = line.strip()
        if stripped == "**Do this.**":
            current = "do"
            continue
        if stripped == "**How to verify.**":
            current = "verify"
            continue
        if stripped == "**Watch for.**":
            current = "watch"
            continue
        collected[current].append(line)
    for key in parts:
        parts[key] = "\n".join(collected[key]).strip()
    return parts


def render_item(item: Item) -> str:
    parts = split_body(item.body)
    optional_badge = (
        '<span class="badge optional">Optional</span>' if item.optional else ""
    )
    maturity = html.escape(item.fields["Maturity"])
    kind = html.escape(item.fields["Kind"].replace("-", " "))
    rows = []
    for label in ("Access needed", "Maintenance", "Sources"):
        rows.append(
            "<div class='meta-row'>"
            f"<dt>{html.escape(label)}</dt>"
            f"<dd>{md_inline(item.fields[label])}</dd>"
            "</div>"
        )
    extra = f"<div class='prose'>{md_blocks(parts['other'])}</div>" if parts["other"] else ""
    watch = (
        f"<div class='watch'><h4>Watch for</h4>{md_blocks(parts['watch'])}</div>"
        if parts["watch"]
        else ""
    )
    return f"""
<article class="item level-{item.level} pillar-{html.escape(item.pillar.lower())}" id="{html.escape(item.item_id.lower())}">
  <header class="item-head">
    <span class="checkbox" aria-hidden="true"></span>
    <h3>{html.escape(item.item_id)}. {html.escape(item.title)}</h3>
    <div class="badges">
      <span class="badge level level-{item.level}">Level {item.level}</span>
      <span class="badge pillar">{html.escape(item.pillar)}</span>
      <span class="badge kind">{kind}</span>
      <span class="badge maturity">{maturity}</span>
      {optional_badge}
    </div>
  </header>
  <dl class="meta">{''.join(rows)}</dl>
  {extra}
  <div class="do-this"><h4>Do this</h4>{md_blocks(parts['do'])}</div>
  <div class="verify"><h4>How to verify</h4>{md_blocks(parts['verify'])}</div>
  {watch}
</article>
"""


def view_banner(view: str, levels: set[int] | None, item_count: int) -> str:
    if view == "all":
        label = "Complete checklist (all capability levels)"
        detail = (
            "This view includes every item. Level badges mark the access each "
            "action typically needs; they are not scores."
        )
    elif view == "level-1":
        label = "Level 1 view — publish or update served files"
        detail = (
            "Only Level 1 items are included. These are file-shaped actions. "
            "Publishing a file may still require an administrator. Higher-level "
            "configuration and services appear in the complete checklist."
        )
    else:
        label = "Levels 1–2 view — files and platform configuration"
        detail = (
            "Includes Level 1 and Level 2 items. Actions that require writing "
            "or operating software (Level 3) are omitted here; see the complete "
            "checklist for APIs, MCP, and validation tooling."
        )
    extra = ""
    if levels:
        extra = f" Showing {item_count} item{'s' if item_count != 1 else ''}."
    return (
        f'<aside class="view-banner"><p><strong>{html.escape(label)}.</strong> '
        f"{html.escape(detail)}{html.escape(extra)}</p></aside>"
    )


def render_html(
    doc: Document,
    view: str,
    levels: set[int] | None,
    revision: Revision | None = None,
) -> str:
    if revision is None:
        revision = resolve_revision()
    sections_html = []
    for section in doc.sections:
        items_html = "".join(render_item(item) for item in section.items)
        intro = f'<div class="section-intro">{md_blocks(section.intro)}</div>' if section.intro else ""
        if not section.items and not section.intro:
            continue
        sections_html.append(
            f'<section class="pillar-section">'
            f"<h2>{html.escape(section.title)}</h2>"
            f"{intro}{items_html}</section>"
        )
    preamble_html = md_blocks(doc.preamble)
    title = "Repository checklist: making your repository more accessible to SI"
    date_meta = ""
    if revision.date != "unknown":
        # Noon UTC avoids date-only values being treated as midnight UTC,
        # which would display as the previous local calendar day (for example
        # 2026-11-06 -> 2026-11-05 18:00 CST).
        date_stamp = html.escape(f"{revision.date}T12:00:00Z")
        date_meta = (
            f'  <meta name="dcterms.created" content="{date_stamp}">\n'
            f'  <meta name="dcterms.modified" content="{date_stamp}">\n'
        )
    source_line = (
        f"Checklist source {revision.version}, dated {revision.date} "
        f"({revision.date_source}) · not a certification"
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
{date_meta}  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header class="cover">
    <p class="kicker">NIAID Blueprint webinar companion · 6 November 2026</p>
    <p class="generated">{html.escape(source_line)}</p>
  </header>
  {view_banner(view, levels, len(doc.items))}
  <div class="preamble">{preamble_html}</div>
  {''.join(sections_html)}
  <footer class="colophon">
    <p>Generated from <code>docs/checklist/checklist.md</code>. Edit the Markdown, then rebuild.
    Empty boxes are for print or local copies; this PDF is not a fillable form.</p>
  </footer>
</body>
</html>
"""


VIEWS: dict[str, set[int] | None] = {
    "all": None,
    "level-1": {1},
    "through-2": {1, 2},
}

OUTPUT_STEMS = {
    "all": "checklist",
    "level-1": "checklist-level-1",
    "through-2": "checklist-through-level-2",
}


def extract_links(doc: Document) -> list[tuple[str, str, str]]:
    """Return (item_or_section, label, url) for every Markdown link in fields and bodies."""
    found: list[tuple[str, str, str]] = []
    blobs: list[tuple[str, str]] = [("preamble", doc.preamble)]
    for section in doc.sections:
        blobs.append((section.title, section.intro))
        for item in section.items:
            blobs.append((item.item_id, item.body))
            for value in item.fields.values():
                blobs.append((item.item_id, value))
    for origin, text in blobs:
        for label, url in LINK_RE.findall(text):
            found.append((origin, label, url))
    return found


def validate_document(doc: Document, source_dir: Path) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    if not doc.items:
        errors.append("no checklist items found")
    for item in doc.items:
        if item.item_id in seen:
            errors.append(f"duplicate id {item.item_id}")
        seen.add(item.item_id)
        if not split_body(item.body)["do"]:
            errors.append(f"{item.item_id} is missing 'Do this'")
        if not split_body(item.body)["verify"]:
            errors.append(f"{item.item_id} is missing 'How to verify'")
    for origin, _label, url in extract_links(doc):
        if url.startswith("http://") or url.startswith("https://"):
            continue
        path_part = url.split("#", 1)[0]
        if not path_part:
            continue
        target = (source_dir / path_part).resolve()
        if not target.exists():
            errors.append(f"{origin} links to missing file {url}")
    return errors


def write_view(
    doc: Document,
    view: str,
    write_html: bool,
    write_pdf: bool,
    revision: Revision | None = None,
) -> dict[str, Path]:
    if revision is None:
        revision = resolve_revision()
    levels = VIEWS[view]
    filtered = filter_document(doc, levels)
    html_text = render_html(filtered, view, levels, revision)
    stem = OUTPUT_STEMS[view]
    DIST.mkdir(parents=True, exist_ok=True)
    written: dict[str, Path] = {}
    html_path = DIST / f"{stem}.html"
    if write_html:
        html_path.write_text(
            relocate_html_urls(html_text, HERE, DIST),
            encoding="utf-8",
        )
        # Copy CSS next to HTML so a browser can open the file directly.
        dest_css = DIST / "style.css"
        dest_css.write_text(STYLE.read_text(encoding="utf-8"), encoding="utf-8")
        written["html"] = html_path
    if write_pdf:
        pdf_path = DIST / f"{stem}.pdf"
        # Keep PDF /ID stable across rebuilds of the same HTML.
        identifier = hashlib.sha256(html_text.encode("utf-8")).digest()
        HTML(string=html_text, base_url=str(HERE)).write_pdf(
            pdf_path,
            stylesheets=[CSS(filename=str(STYLE))],
            pdf_identifier=identifier,
        )
        written["pdf"] = pdf_path
    return written


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--view",
        choices=[*VIEWS, "all-views"],
        default="all-views",
        help="Which level filter to render (default: every view)",
    )
    parser.add_argument("--html-only", action="store_true")
    parser.add_argument("--pdf-only", action="store_true")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Parse and validate the source without writing output",
    )
    parser.add_argument(
        "--date",
        metavar="YYYY-MM-DD",
        help=(
            "Source/review date printed in the output. Default is the last git "
            "commit date of checklist.md (or SOURCE_DATE_EPOCH). This is not "
            "today's build date and not an evidence date for cited standards."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    source_text = SOURCE.read_text(encoding="utf-8")
    doc = parse_document(source_text)
    revision = resolve_revision(cli_date=args.date, source_text=source_text)
    errors = validate_document(doc, HERE)
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    if args.check:
        print(
            f"ok: {len(doc.items)} items in {len(doc.sections)} sections; "
            f"source {revision.version} dated {revision.date} ({revision.date_source})"
        )
        return 0
    write_html = not args.pdf_only
    write_pdf = not args.html_only
    views = list(VIEWS) if args.view == "all-views" else [args.view]
    for view in views:
        written = write_view(doc, view, write_html, write_pdf, revision)
        for kind, path in written.items():
            print(f"wrote {kind}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
