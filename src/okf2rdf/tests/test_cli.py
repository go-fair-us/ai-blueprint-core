from __future__ import annotations

from pathlib import Path

from okf2rdf.cli import main
from rdflib import Graph

FIXTURE = Path(__file__).parent / "fixtures" / "mini_bundle"


def test_cli_turtle(tmp_path: Path):
    out = tmp_path / "out.ttl"
    rc = main(
        [
            "--bundle",
            str(FIXTURE),
            "--base",
            "https://example.org/b/",
            "--out",
            str(out),
            "--format",
            "turtle",
            "--name",
            "Mini",
        ]
    )
    assert rc == 0
    assert out.exists()
    g = Graph()
    g.parse(out, format="turtle")
    assert len(g) > 10


def test_cli_jsonld(tmp_path: Path):
    out = tmp_path / "out.jsonld"
    rc = main(
        [
            "--bundle",
            str(FIXTURE),
            "--base",
            "https://example.org/b/",
            "--out",
            str(out),
            "--format",
            "json-ld",
        ]
    )
    assert rc == 0
    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert "@context" in text or "schema.org" in text
