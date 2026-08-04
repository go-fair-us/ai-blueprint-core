"""Unit tests for genMeta artifact helpers (no Herdr required)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

GENMETA = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GENMETA))

from defs.artifacts import (  # noqa: E402
    ensure_record_jsonld,
    extract_jsonld_from_text,
    new_run_dir,
)


def test_extract_jsonld_from_fenced_block() -> None:
    text = """
Here is the record:

```json
{
  "@context": "https://schema.org/",
  "@type": "Dataset",
  "name": "Demo",
  "description": "A description that is definitely longer than fifty characters for SHACL.",
  "url": "https://example.org/d"
}
```
"""
    data = extract_jsonld_from_text(text)
    assert data is not None
    assert data["@type"] == "Dataset"
    assert data["name"] == "Demo"


def test_ensure_record_recovers_from_transcript(tmp_path: Path) -> None:
    run = new_run_dir(tmp_path, label="test-run")
    transcript = (
        "```json\n"
        + json.dumps(
            {
                "@context": "https://schema.org/",
                "@type": "Dataset",
                "name": "X",
                "description": "Y" * 60,
                "url": "https://ex.org",
            }
        )
        + "\n```\n"
    )
    path = ensure_record_jsonld(run, transcript=transcript)
    assert path.is_file()
    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert loaded["name"] == "X"


def test_ensure_record_raises_without_data(tmp_path: Path) -> None:
    run = new_run_dir(tmp_path, label="empty-run")
    with pytest.raises(FileNotFoundError):
        ensure_record_jsonld(run, transcript="no json here")
