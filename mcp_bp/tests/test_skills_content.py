"""Tests for Agent Skill catalog, safe file reads, and SHACL wrap."""

from __future__ import annotations

from pathlib import Path

import pytest

from mcp_bp import skills_content
from mcp_bp.skills_content import SkillsError

REPO_ROOT = Path(__file__).resolve().parents[2]
REAL_SKILLS = REPO_ROOT / "niaid-blueprint" / "skills"
VALID_JSONLD = (
    REAL_SKILLS / "niaid-bp-validation" / "tests" / "fixtures" / "valid_dataset.jsonld"
)
INVALID_JSONLD = (
    REAL_SKILLS / "niaid-bp-validation" / "tests" / "fixtures" / "invalid_dataset.jsonld"
)


def test_list_skills(content_tree) -> None:
    entries = skills_content.list_skills()
    names = {e["name"] for e in entries}
    assert names == {"niaid-bp-fair-assess", "niaid-bp-validation"}
    by_name = {e["name"]: e for e in entries}
    assert "FAIR assessment" in by_name["niaid-bp-fair-assess"]["description"]
    assert by_name["niaid-bp-fair-assess"]["when_to_use"]
    assert by_name["niaid-bp-fair-assess"]["has_references"] is True
    assert by_name["niaid-bp-fair-assess"]["has_scripts"] is False
    assert by_name["niaid-bp-validation"]["has_scripts"] is True


def test_read_skill_body(content_tree) -> None:
    body = skills_content.read_skill("niaid-bp-fair-assess")
    assert body.startswith("---")
    assert "interview-phases.md" in body


def test_read_skill_file_reference(content_tree) -> None:
    payload = skills_content.read_skill_file(
        "niaid-bp-fair-assess", "references/interview-phases.md"
    )
    assert payload["path"] == "references/interview-phases.md"
    assert "Phase 1" in payload["text"]


def test_read_skill_rejects_unknown(content_tree) -> None:
    with pytest.raises(SkillsError, match="Unknown skill"):
        skills_content.read_skill("niaid-bp-nope")


def test_read_skill_rejects_traversal_name(content_tree) -> None:
    with pytest.raises(SkillsError, match="Invalid skill name"):
        skills_content.read_skill("../docs")


def test_read_skill_file_rejects_traversal(content_tree) -> None:
    with pytest.raises(SkillsError, match="escapes"):
        skills_content.read_skill_file(
            "niaid-bp-fair-assess", "../niaid-bp-validation/SKILL.md"
        )


def test_read_skill_file_rejects_disallowed_extension(content_tree) -> None:
    with pytest.raises(SkillsError, match="extensions"):
        skills_content.read_skill_file("niaid-bp-validation", "secret.bin")


def test_read_skill_file_missing(content_tree) -> None:
    with pytest.raises(SkillsError, match="not found"):
        skills_content.read_skill_file(
            "niaid-bp-fair-assess", "references/missing.md"
        )


def test_skills_stats(content_tree) -> None:
    stats = skills_content.skills_stats()
    assert stats["count"] == 2
    assert stats["root_exists"] is True


@pytest.mark.skipif(not VALID_JSONLD.is_file(), reason="validation fixtures missing")
def test_validate_dataset_conforms(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(skills_content, "SKILLS_DIR", REAL_SKILLS)
    graph = VALID_JSONLD.read_text(encoding="utf-8")
    summary = skills_content.validate_dataset(graph, data_format="json-ld")
    assert summary["conforms"] is True
    assert summary["n_violations"] == 0
    assert "blueprint-required.ttl" in summary["shape"]


@pytest.mark.skipif(not INVALID_JSONLD.is_file(), reason="validation fixtures missing")
def test_validate_dataset_finds_violations(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(skills_content, "SKILLS_DIR", REAL_SKILLS)
    graph = INVALID_JSONLD.read_text(encoding="utf-8")
    summary = skills_content.validate_dataset(graph)
    assert summary["conforms"] is False
    assert summary["n_violations"] >= 1
    assert summary["results"]


def test_validate_dataset_rejects_empty(content_tree) -> None:
    with pytest.raises(SkillsError, match="empty"):
        skills_content.validate_dataset("  ")


def test_validate_dataset_rejects_bad_format(content_tree) -> None:
    with pytest.raises(SkillsError, match="Unsupported"):
        skills_content.validate_dataset("{}", data_format="csv")


@pytest.mark.skipif(not VALID_JSONLD.is_file(), reason="validation fixtures missing")
def test_validate_dataset_refuses_remote_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A crafted @context must not turn validation into an outbound request.

    ``graph`` is untrusted -- it is whatever the caller pasted -- and rdflib
    would otherwise dereference the IRI while parsing.
    """
    import socket

    monkeypatch.setattr(skills_content, "SKILLS_DIR", REAL_SKILLS)

    def _refuse(*args, **kwargs):  # noqa: ANN002, ANN003
        raise AssertionError(f"unexpected outbound connection: {args!r}")

    monkeypatch.setattr(socket.socket, "connect", _refuse)
    monkeypatch.setattr(socket, "getaddrinfo", _refuse)

    graph = (
        '{"@context": "https://attacker.example/ctx.jsonld",'
        ' "@type": "Dataset", "name": "x"}'
    )
    with pytest.raises(SkillsError, match="Refusing to dereference"):
        skills_content.validate_dataset(graph, data_format="json-ld")
