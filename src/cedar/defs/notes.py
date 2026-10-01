"""Render extract notes as Markdown."""
from __future__ import annotations

from defs.models import DroppedValue, FetchedPage, FieldNote


def render_notes(
    *,
    start_url: str | None,
    pages: list[FetchedPage],
    notes: list[FieldNote],
    dropped: list[DroppedValue],
    evidence_summary: str | None,
) -> str:
    lines = ["# CEDAR extract notes", ""]
    if start_url:
        lines.append(f"Start URL: {start_url}")
        lines.append("")
    lines.append("## Pages")
    for page in pages:
        status = "ok" if page.ok else f"unreadable: {page.error}"
        lines.append(f"- depth {page.depth}: {page.url} ({status})")
    if evidence_summary:
        lines.extend(["", "## Gather", evidence_summary.strip(), ""])

    found = [n for n in notes if n.status == "found"]
    missing = [n for n in notes if n.status == "missing"]
    lines.append("## Found")
    if found:
        for note in found:
            quote = f' — "{note.quote}"' if note.quote else ""
            src = f" ({note.source_url})" if note.source_url else ""
            lines.append(f"- {note.field}{src}{quote}")
    else:
        lines.append("- (none reported by extractors)")
    lines.append("")
    lines.append("## Missing")
    if missing:
        for note in missing:
            lines.append(f"- {note.field}")
    else:
        lines.append("- (none reported by extractors)")
    lines.append("")
    lines.append("## Ungrounded (dropped)")
    if dropped:
        for item in dropped:
            lines.append(f"- {item.field}: `{item.value}`")
    else:
        lines.append("- none")
    lines.append("")
    unread = [p for p in pages if p.error]
    lines.append("## Unreadable")
    if unread:
        for page in unread:
            lines.append(f"- {page.url}: {page.error}")
    else:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)
