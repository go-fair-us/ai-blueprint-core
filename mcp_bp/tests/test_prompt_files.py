"""Prompt file tools and the prompts:// resource, including nested evals."""

from __future__ import annotations

import asyncio

import pytest

from mcp_bp import server
from mcp_bp.content import ContentError


def test_read_prompt_file_serves_nested_eval(content_tree) -> None:
    prompts = content_tree["prompts"]
    (prompts / "evals").mkdir()
    (prompts / "evals" / "sitemap.md").write_text(
        "# Sitemap eval\n\nWell formed.\n", encoding="utf-8"
    )

    listed = {row["path"] for row in server.list_prompt_files()}
    assert "evals/sitemap.md" in listed
    assert "Sitemap eval" in server.read_prompt_file("evals/sitemap.md")


def test_read_prompt_file_accepts_persona_name(content_tree) -> None:
    text = server.read_prompt_file("fair_web_assessor")
    assert "FAIR assessor" in text


def test_read_prompt_file_rejects_traversal(content_tree) -> None:
    with pytest.raises(ValueError, match="escapes"):
        server.read_prompt_file("../docs/secret.md")


def test_prompts_resource_reads_nested_and_keeps_persona_list(content_tree) -> None:
    prompts = content_tree["prompts"]
    (prompts / "evals").mkdir()
    (prompts / "evals" / "robots-policy.md").write_text(
        "# Robots eval\n\nContent-Usage.\n", encoding="utf-8"
    )

    async def _read(uri: str) -> str:
        result = await server.mcp.read_resource(uri)
        return str(result.contents[0].content)

    body = asyncio.run(_read("prompts://evals/robots-policy.md"))
    assert "Robots eval" in body

    catalog = asyncio.run(_read("prompts://list"))
    assert "fair_assessment_interview" in catalog
    assert "work_plan_interview" in catalog

    persona = asyncio.run(_read("prompts://fair_web_assessor"))
    assert "FAIR assessor" in persona


def test_prompts_resource_unknown_path(content_tree) -> None:
    async def _read() -> None:
        await server.mcp.read_resource("prompts://evals/missing.md")

    with pytest.raises(Exception) as exc_info:
        asyncio.run(_read())
    assert isinstance(exc_info.value.__cause__, ContentError)
    assert "evals/missing.md" in str(exc_info.value.__cause__)
