"""Tests for safe path resolution, listing, and reading."""

from __future__ import annotations

from pathlib import Path

import pytest

from mcp_bp import config, content
from mcp_bp.content import ContentError


def test_list_markdown_finds_md_and_ignores_other(content_tree) -> None:
    entries = content.list_markdown(content_tree["docs"])
    paths = {entry.path for entry in entries}

    assert config.BLUEPRINT_SPEC_RELPATH in paths
    assert "sub/extra.md" in paths
    assert "ignore.pdf" not in paths


def test_title_derived_from_first_heading(content_tree) -> None:
    entries = {e.path: e for e in content.list_markdown(content_tree["docs"])}
    assert entries["sub/extra.md"].title == "Extra Doc"


def test_read_markdown_roundtrip(content_tree) -> None:
    text = content.read_markdown(content_tree["docs"], "sub/extra.md")
    assert "citation guidance" in text


def test_safe_resolve_rejects_traversal(content_tree) -> None:
    with pytest.raises(ContentError):
        content.safe_resolve(content_tree["docs"], "../prompts/x.md")


def test_safe_resolve_rejects_non_markdown(content_tree) -> None:
    with pytest.raises(ContentError):
        content.safe_resolve(content_tree["docs"], "ignore.pdf")


def test_nested_prompt_markdown_roundtrip(content_tree) -> None:
    prompts = content_tree["prompts"]
    (prompts / "evals").mkdir()
    (prompts / "evals" / "sitemap.md").write_text(
        "# Sitemap eval\n\nCheck the sitemap.\n", encoding="utf-8"
    )
    paths = {entry.path for entry in content.list_prompt_files()}
    assert "evals/sitemap.md" in paths
    assert "Sitemap eval" in content.read_prompt_file("evals/sitemap.md")


def test_repo_eval_prompts_are_on_disk() -> None:
    root = Path(__file__).resolve().parents[2] / "prompts"
    paths = {entry.path for entry in content.list_markdown(root)}
    for rel in (
        "evals/sitemap.md",
        "evals/robots-policy.md",
        "evals/llms-txt.md",
        "workPlanSpec.md",
    ):
        assert rel in paths


def test_read_missing_file_raises(content_tree) -> None:
    with pytest.raises(ContentError):
        content.read_markdown(content_tree["docs"], "nope.md")
