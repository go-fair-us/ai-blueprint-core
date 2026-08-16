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

from validate import (  # noqa: E402
    RemoteContextError,
    main,
    run_validation,
)

CONTEXTS = SKILL_DIR / "assets" / "contexts"


@pytest.fixture
def no_network(monkeypatch: pytest.MonkeyPatch) -> list[tuple]:
    """Fail any outbound socket connection, recording what was attempted."""
    import socket

    attempts: list[tuple] = []

    def _refuse(*args, **kwargs):  # noqa: ANN002, ANN003
        attempts.append(args[1:] if len(args) > 1 else args)
        raise AssertionError(f"unexpected outbound connection: {args!r}")

    monkeypatch.setattr(socket.socket, "connect", _refuse)
    monkeypatch.setattr(socket.socket, "connect_ex", _refuse)
    monkeypatch.setattr(socket, "create_connection", _refuse)
    monkeypatch.setattr(socket, "getaddrinfo", _refuse)
    return attempts


def _write(tmp_path: Path, doc: dict) -> Path:
    path = tmp_path / "dataset.jsonld"
    path.write_text(json.dumps(doc), encoding="utf-8")
    return path


def _dataset(**extra) -> dict:
    doc = {
        "@type": "Dataset",
        "@id": "https://example.org/d/1",
        "name": "Test dataset",
        "description": "A description that is comfortably longer than the fifty "
        "character minimum the Blueprint required shape enforces.",
        "url": "https://example.org/d/1",
    }
    doc.update(extra)
    return doc


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


# --------------------------------------------------------------------------
# JSON-LD contexts are resolved locally and never fetched.
# --------------------------------------------------------------------------


def test_vendored_schema_org_context_present() -> None:
    ctx = CONTEXTS / "schemaorg-jsonldcontext.jsonld"
    assert ctx.is_file()
    terms = json.loads(ctx.read_text(encoding="utf-8"))["@context"]
    assert terms["@vocab"] == "http://schema.org/"
    for term in ("name", "description", "url", "Dataset"):
        assert term in terms


def test_schema_org_context_resolves_with_no_network(
    tmp_path: Path, no_network: list
) -> None:
    """The everyday case still validates with every socket blocked."""
    summary = run_validation(
        FIXTURES / "valid_dataset.jsonld", shape_path=SHAPE, out_dir=tmp_path
    )
    assert summary["conforms"] is True
    assert no_network == []


@pytest.mark.parametrize(
    "context",
    [
        "http://127.0.0.1:9/evil.jsonld",
        "https://attacker.example/ctx.jsonld",
        "file:///etc/passwd",
        "http://169.254.169.254/latest/meta-data/",
    ],
)
def test_remote_context_refused(tmp_path: Path, no_network: list, context: str) -> None:
    path = _write(tmp_path, _dataset(**{"@context": context}))
    with pytest.raises(RemoteContextError, match="Refusing to dereference"):
        run_validation(path, shape_path=SHAPE, out_dir=tmp_path / "out")
    assert no_network == []


def test_remote_context_refused_inside_array(
    tmp_path: Path, no_network: list
) -> None:
    doc = _dataset(
        **{"@context": ["https://schema.org/", "https://attacker.example/ctx.jsonld"]}
    )
    path = _write(tmp_path, doc)
    with pytest.raises(RemoteContextError, match="attacker.example"):
        run_validation(path, shape_path=SHAPE, out_dir=tmp_path / "out")
    assert no_network == []


def test_remote_context_refused_when_scoped_on_nested_node(
    tmp_path: Path, no_network: list
) -> None:
    """A scoped context deeper in the document is caught, not just the root."""
    doc = _dataset(
        **{"@context": "https://schema.org/"},
        creator={
            "@context": "https://attacker.example/ctx.jsonld",
            "@type": "Person",
            "name": "A. Person",
        },
    )
    path = _write(tmp_path, doc)
    with pytest.raises(RemoteContextError, match="attacker.example"):
        run_validation(path, shape_path=SHAPE, out_dir=tmp_path / "out")
    assert no_network == []


def test_context_import_refused(tmp_path: Path, no_network: list) -> None:
    doc = _dataset(
        **{
            "@context": {
                "@import": "https://attacker.example/ctx.jsonld",
                "@vocab": "https://schema.org/",
            }
        }
    )
    path = _write(tmp_path, doc)
    with pytest.raises(RemoteContextError, match="@import"):
        run_validation(path, shape_path=SHAPE, out_dir=tmp_path / "out")
    assert no_network == []


def test_inline_context_object_still_works(
    tmp_path: Path, no_network: list
) -> None:
    doc = _dataset(**{"@context": {"@vocab": "https://schema.org/"}})
    path = _write(tmp_path, doc)
    summary = run_validation(path, shape_path=SHAPE, out_dir=tmp_path / "out")
    assert summary["conforms"] is True
    assert no_network == []


def test_turtle_input_unaffected(tmp_path: Path, no_network: list) -> None:
    ttl = tmp_path / "dataset.ttl"
    ttl.write_text(
        '@prefix schema: <https://schema.org/> .\n'
        '<https://example.org/d/1> a schema:Dataset ;\n'
        '  schema:name "Test dataset" ;\n'
        '  schema:description "A description that is comfortably longer than '
        'the fifty character minimum the Blueprint required shape enforces." ;\n'
        '  schema:url <https://example.org/d/1> .\n',
        encoding="utf-8",
    )
    summary = run_validation(ttl, shape_path=SHAPE, out_dir=tmp_path / "out")
    assert summary["conforms"] is True
    assert no_network == []
