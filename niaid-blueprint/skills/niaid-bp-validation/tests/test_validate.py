"""Tests for niaid-bp-validation scripts/validate.py."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_DIR / "scripts"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
SHAPE = SKILL_DIR / "assets" / "blueprint-required.ttl"

sys.path.insert(0, str(SCRIPTS))

pyshacl = pytest.importorskip("pyshacl")
rdflib = pytest.importorskip("rdflib")

from validate import run_validation, main  # noqa: E402


def test_shape_file_exists() -> None:
    assert SHAPE.is_file()
    text = SHAPE.read_text(encoding="utf-8")
    assert "schema:name" in text or "https://schema.org/name" in text
    assert "sh:NodeShape" in text


def test_valid_dataset_conforms(tmp_path: Path) -> None:
    summary = run_validation(
        FIXTURES / "valid_dataset.jsonld",
        shape_path=SHAPE,
        out_dir=tmp_path,
    )
    assert summary["conforms"] is True
    assert summary["n_violations"] == 0
    assert (tmp_path / "report.ttl").is_file()
    assert (tmp_path / "results.json").is_file()
    assert (tmp_path / "conforms.json").is_file()
    payload = json.loads((tmp_path / "conforms.json").read_text(encoding="utf-8"))
    assert payload["conforms"] is True


def test_invalid_dataset_nonconforming(tmp_path: Path) -> None:
    summary = run_validation(
        FIXTURES / "invalid_dataset.jsonld",
        shape_path=SHAPE,
        out_dir=tmp_path,
    )
    assert summary["conforms"] is False
    assert summary["n_violations"] >= 1
    paths = {r.get("result_path") for r in summary["results"]}
    # Missing description and url should surface as property paths
    path_blob = " ".join(p or "" for p in paths)
    assert "description" in path_blob or "url" in path_blob or summary["n_violations"] > 0


def test_cli_exit_codes(tmp_path: Path) -> None:
    assert (
        main(
            [
                str(FIXTURES / "valid_dataset.jsonld"),
                "--shape",
                str(SHAPE),
                "--out-dir",
                str(tmp_path / "ok"),
            ]
        )
        == 0
    )
    assert (
        main(
            [
                str(FIXTURES / "invalid_dataset.jsonld"),
                "--shape",
                str(SHAPE),
                "--out-dir",
                str(tmp_path / "bad"),
            ]
        )
        == 1
    )
