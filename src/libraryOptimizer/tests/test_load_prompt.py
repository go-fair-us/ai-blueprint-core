"""Tests for front-matter strip and # Prompt extraction."""
from __future__ import annotations

from pathlib import Path

import pytest

from defs.load_prompt import (
    extract_prompt_body,
    list_prompt_files,
    load_library_prompt,
    slug_from_path,
    strip_front_matter,
)

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_md(tmp_path: Path) -> Path:
    p = tmp_path / "name-description.md"
    p.write_text(
        """---
type: PromptExample
title: Write a high-quality name + description
tags: [metadata-schema, core-elements, name]
---

# Prompt

You are an expert data steward.

Return JSON with keys: name, description.
""",
        encoding="utf-8",
    )
    return p


def test_strip_front_matter(sample_md: Path):
    text = sample_md.read_text(encoding="utf-8")
    fm, body = strip_front_matter(text)
    assert "title:" in fm
    assert "type: PromptExample" in fm
    assert not body.lstrip().startswith("---")
    assert "# Prompt" in body


def test_extract_prompt_body():
    body = "# Intro\n\nskip\n\n# Prompt\n\nHello world\n\n# Other\n\nnope"
    assert extract_prompt_body(body) == "Hello world"


def test_extract_without_heading():
    assert extract_prompt_body("just text") == "just text"


def test_load_library_prompt(sample_md: Path):
    lp = load_library_prompt(sample_md)
    assert "expert data steward" in lp.body
    assert "---" not in lp.body
    assert lp.title.startswith("Write a high-quality")
    assert "metadata-schema" in lp.tags
    assert lp.slug == "name-description"


def test_slug_from_nested_path(tmp_path: Path):
    root = tmp_path / "prompt_examples"
    nested = root / "metadata-schema" / "core-elements" / "name-description.md"
    nested.parent.mkdir(parents=True)
    nested.write_text("# Prompt\n\nhi\n", encoding="utf-8")
    assert slug_from_path(nested, root) == "metadata-schema-core-elements-name-description"


def test_load_real_okf_example_if_present():
    repo = Path(__file__).resolve().parents[3]
    example = (
        repo
        / "okf"
        / "prompt_examples"
        / "metadata-schema"
        / "core-elements"
        / "name-description.md"
    )
    if not example.is_file():
        pytest.skip("OKF example not in tree")
    lp = load_library_prompt(example)
    assert "NIAID Blueprint" in lp.body or "data steward" in lp.body.lower()
    assert not lp.body.startswith("---")
    assert "name-description" in lp.slug


def test_list_prompt_files_skips_readme(tmp_path: Path):
    (tmp_path / "README.md").write_text("# hi\n", encoding="utf-8")
    leaf = tmp_path / "a" / "b.md"
    leaf.parent.mkdir()
    leaf.write_text("# Prompt\n\nx\n", encoding="utf-8")
    files = list_prompt_files(tmp_path)
    assert files == [leaf.resolve()]
