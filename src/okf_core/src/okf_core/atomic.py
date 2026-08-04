"""Parse ``# Atomic concepts`` tables from OKF concept bodies.

NIAID Blueprint bundles use a uniform table shape::

    # Atomic concepts

    | # | Concept | Lines |
    |---|---------|-------|
    | 118 | Claim text… | 180 |
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_ATOMIC_HEADING_RE = re.compile(r"^#\s+Atomic concepts\s*$", re.MULTILINE)
_NEXT_HEADING_RE = re.compile(r"^#\s+", re.MULTILINE)
# Data row: | number | concept text | lines |
_ROW_RE = re.compile(
    r"^\|\s*(\d+)\s*\|\s*(.+?)\s*\|\s*([^|]+?)\s*\|\s*$",
    re.MULTILINE,
)


@dataclass(frozen=True)
class AtomicConcept:
    """One row from an Atomic concepts table."""

    number: int
    text: str
    source_lines: str
    parent_id: str

    @property
    def concept_id(self) -> str:
        """Path-style id relative to bundle: ``atomic/{number}``."""
        return f"atomic/{self.number}"


def parse_atomic_concepts(body: str, parent_id: str) -> list[AtomicConcept]:
    """Extract atomic concept rows from a concept document body.

    Returns an empty list when the heading or table is missing.
    """
    if not body:
        return []
    m = _ATOMIC_HEADING_RE.search(body)
    if not m:
        return []
    rest = body[m.end() :]
    # Stop at the next AT-level AT heading (e.g. unlikely) — tables usually
    # run to footnotes or EOF. Footnote defs start with [^ not #.
    next_h = _NEXT_HEADING_RE.search(rest)
    if next_h:
        rest = rest[: next_h.start()]

    out: list[AtomicConcept] = []
    seen: set[int] = set()
    for row in _ROW_RE.finditer(rest):
        num = int(row.group(1))
        text = row.group(2).strip()
        lines = row.group(3).strip()
        if not text:
            continue
        if num in seen:
            # Keep first occurrence; duplicates are rare / invalid for NIAID
            continue
        seen.add(num)
        out.append(
            AtomicConcept(
                number=num,
                text=text,
                source_lines=lines,
                parent_id=parent_id,
            )
        )
    out.sort(key=lambda a: a.number)
    return out


def count_atomics(concepts: list) -> int:
    """Sum atomic rows across a list of OkfConcept-like objects with ``.atomics``."""
    return sum(len(getattr(c, "atomics", []) or []) for c in concepts)
