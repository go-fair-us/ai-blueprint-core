"""Tests for guidance section slicing."""
from __future__ import annotations

from pathlib import Path

from defs.guidance import build_guidance_context, clear_guidance_cache, slice_by_keywords
from defs import paths as pathconf


def test_slice_by_keywords_keeps_matching_sections():
    md = """# Overview

Ignore me.

# Metadata Schema

Keep table 1 details here.

# Random Notes

Nothing relevant.

# Persistent Identifiers

DOI and ORCID guidance.
"""
    out = slice_by_keywords(md, ["metadata", "identifier", "doi"])
    assert "Keep table 1" in out
    assert "DOI and ORCID" in out
    assert "Ignore me" not in out
    assert "Nothing relevant" not in out


def test_slice_fallback_when_no_match():
    md = "# Only\n\nzzz\n"
    out = slice_by_keywords(md, ["never-match-this-keyword-xyz"], fallback_chars=100)
    assert "zzz" in out


def test_build_guidance_context(tmp_path: Path):
    clear_guidance_cache()
    pathconf.configure_paths(workdir=tmp_path, announce=False)

    bp = tmp_path / "blueprint.md"
    wp = tmp_path / "workplans.md"
    bp.write_text(
        "# Intro\n\nskip\n\n# Metadata Schema\n\nBlueprint metadata rules.\n",
        encoding="utf-8",
    )
    wp.write_text(
        "# Other\n\nskip\n\n# FAIR repository practices\n\nWork plan FAIR notes.\n",
        encoding="utf-8",
    )

    ctx = build_guidance_context(
        blueprint_path=bp,
        workplans_path=wp,
        keep_keywords=["metadata", "fair", "repository"],
        max_chars=5000,
        refresh=True,
    )
    assert "## Blueprint" in ctx
    assert "## Work Plans" in ctx
    assert "Blueprint metadata rules" in ctx
    assert "Work plan FAIR notes" in ctx
    assert (tmp_path / "guidance.md").is_file()
    clear_guidance_cache()
