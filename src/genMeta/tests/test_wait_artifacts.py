"""Artifact-gated wait helpers (no Herdr required)."""

from __future__ import annotations

import json
import sys
import threading
import time
from pathlib import Path

import pytest

GENMETA = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GENMETA))

from defs.artifacts import (  # noqa: E402
    is_parseable_jsonld,
    new_run_dir,
    notes_path,
    record_path,
    wait_for_extract_artifacts,
    wait_for_record_update,
)


def _write_record(path: Path, *, url: str = "https://example.org/d") -> None:
    data = {
        "@context": "https://schema.org/",
        "@type": "Dataset",
        "name": "Demo",
        "description": "A description that is definitely longer than fifty characters.",
        "url": url,
    }
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def test_wait_for_extract_artifacts(tmp_path: Path) -> None:
    run = new_run_dir(tmp_path, label="wait-extract")
    not_before = time.time()

    def _writer() -> None:
        time.sleep(0.4)
        _write_record(record_path(run))
        notes_path(run).write_text("# notes\n", encoding="utf-8")

    threading.Thread(target=_writer, daemon=True).start()
    out = wait_for_extract_artifacts(
        run,
        not_before=not_before,
        timeout_s=5.0,
        poll_s=0.1,
        stable_s=0.2,
    )
    assert out == record_path(run)
    assert is_parseable_jsonld(out)


def test_wait_for_extract_timeout(tmp_path: Path) -> None:
    run = new_run_dir(tmp_path, label="wait-timeout")
    with pytest.raises(TimeoutError):
        wait_for_extract_artifacts(
            run,
            not_before=time.time(),
            timeout_s=0.6,
            poll_s=0.1,
            stable_s=0.1,
        )


def test_wait_for_record_update(tmp_path: Path) -> None:
    run = new_run_dir(tmp_path, label="wait-repair")
    rec = record_path(run)
    _write_record(rec)
    prev = rec.stat().st_mtime
    not_before = time.time()

    def _writer() -> None:
        time.sleep(0.4)
        _write_record(rec, url="https://example.org/repaired")

    threading.Thread(target=_writer, daemon=True).start()
    out = wait_for_record_update(
        run,
        previous_mtime=prev,
        not_before=not_before,
        timeout_s=5.0,
        poll_s=0.1,
        stable_s=0.2,
    )
    assert out == rec
    assert "repaired" in rec.read_text(encoding="utf-8")
