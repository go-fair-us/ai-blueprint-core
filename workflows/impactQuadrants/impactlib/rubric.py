"""The versioned effort/impact rubric (rubric.md) and quadrant helpers."""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class Rubric:
    path: Path
    text: str          # body without the front matter (what the model sees)
    version: str
    sha: str

    def tables(self) -> dict[str, list[list[str]]]:
        """{section heading: rows (first row is the header)} for the report appendix."""
        out, head, rows = {}, None, []
        for line in self.text.splitlines():
            if line.startswith("## "):
                if head and rows:
                    out[head] = rows
                head, rows = line[3:].strip(), []
            elif line.startswith("|") and head:
                cells = [c.strip().replace("`", "") for c in line.strip().strip("|").split("|")]
                if not all(set(c) <= set("-: ") for c in cells):
                    rows.append(cells)
        if head and rows:
            out[head] = rows
        return out

    def rules(self) -> list[str]:
        m = re.search(r"^## Rules\s*\n(.*?)(?=^## |\Z)", self.text, re.S | re.M)
        if not m:
            return []
        items = re.split(r"\n\d+\.\s+", "\n" + m.group(1).strip())
        return [re.sub(r"\s+", " ", i).replace("`", "").strip() for i in items if i.strip()]


def load(path: Path | str) -> Rubric:
    path = Path(path)
    raw = path.read_text(encoding="utf-8")
    meta, body = {}, raw
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
    if m:
        meta, body = yaml.safe_load(m.group(1)) or {}, m.group(2)
    version = str(meta.get("version") or "unversioned")
    return Rubric(path=path, text=body.strip() + "\n", version=version,
                  sha=hashlib.sha256(raw.encode()).hexdigest()[:12])


def quadrant(x: float, y: float, names: dict) -> str:
    """Region rules as in rubric.md: x < 0 is left, y >= 0 is top."""
    key = ("top_" if y >= 0 else "bottom_") + ("left" if x < 0 else "right")
    return names.get(key, key)
