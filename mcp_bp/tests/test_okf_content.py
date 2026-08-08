"""Tests for OKF bundle and prompt-example helpers."""

from __future__ import annotations

import pytest

from mcp_bp import okf_content
from mcp_bp.okf_content import OkfError


def test_list_bundles(content_tree) -> None:
    bundles = okf_content.list_bundles()
    assert len(bundles) == 1
    assert bundles[0]["name"] == "niaid_blueprint"
    assert bundles[0]["is_default"] is True
    assert bundles[0]["has_index"] is True


def test_list_concepts_and_filters(content_tree) -> None:
    all_c = okf_content.list_concepts()
    assert len(all_c) == 2
    ids = {c["id"] for c in all_c}
    assert "metadata-schema/requirements" in ids
    assert "metadata-schema/motivation" in ids

    reqs = okf_content.list_concepts(type="Requirements")
    assert len(reqs) == 1
    assert reqs[0]["id"] == "metadata-schema/requirements"
    assert reqs[0]["atomic_count"] == 3

    by_prefix = okf_content.list_concepts(prefix="metadata-schema")
    assert len(by_prefix) == 2

    normative = okf_content.list_concepts(normative=True)
    assert len(normative) == 1
    assert normative[0]["id"] == "metadata-schema/requirements"


def test_get_concept_and_markdown(content_tree) -> None:
    c = okf_content.get_concept("metadata-schema/requirements")
    assert c.title.startswith("Minimal Metadata")
    assert len(c.atomics) == 3
    assert "metadata-schema/motivation" in c.links_to

    data = okf_content.concept_as_dict(c, include_body=False)
    assert "body" not in data
    assert data["atomics"][0]["number"] == 56

    md = okf_content.read_concept_markdown("metadata-schema/requirements")
    assert md.startswith("---")
    assert "Table 1" in md


def test_get_atomic_and_list(content_tree) -> None:
    a = okf_content.get_atomic(57)
    assert "DOI" in a["text"]
    assert a["parent_id"] == "metadata-schema/requirements"
    assert a["source_lines"] == "113"

    hits = okf_content.list_atomics(query="DOI")
    assert any(h["number"] == 57 for h in hits)

    parent_hits = okf_content.list_atomics(parent_id="metadata-schema/motivation")
    assert len(parent_hits) == 1
    assert parent_hits[0]["number"] == 40


def test_get_related(content_tree) -> None:
    related = okf_content.get_related("metadata-schema/requirements")
    assert any(r["id"] == "metadata-schema/motivation" for r in related["links_to"])
    # Reverse: motivation links to requirements
    rev = okf_content.get_related("metadata-schema/motivation")
    assert any(r["id"] == "metadata-schema/requirements" for r in rev["links_to"])


def test_get_requirements_pillar(content_tree) -> None:
    overview = okf_content.get_requirements(None)
    assert "metadata" in overview["pillars"]
    assert overview["available_pillars"]

    meta = okf_content.get_requirements("metadata")
    assert meta["pillar"] == "metadata"
    assert meta["concepts"]
    assert meta["concepts"][0]["id"] == "metadata-schema/requirements"
    assert meta["concepts"][0]["atomics"]


def test_unknown_concept_and_atomic(content_tree) -> None:
    with pytest.raises(OkfError):
        okf_content.get_concept("no/such/concept")
    with pytest.raises(OkfError):
        okf_content.get_atomic(99999)


def test_prompt_examples(content_tree) -> None:
    entries = okf_content.list_prompt_examples()
    assert len(entries) == 1
    assert entries[0]["path"] == "identifier.md"
    body = okf_content.read_prompt_example("identifier.md")
    assert "ImmPort" in body


def test_okf_stats_and_search_chunks(content_tree) -> None:
    stats = okf_content.okf_stats()
    assert stats["enabled"] is True
    assert stats["concepts"] == 2
    assert stats["atomics"] == 4
    assert stats["prompt_examples"] == 1

    chunks = okf_content.search_chunks_for_index()
    sources = {c["chunk_id"] for c in chunks}
    assert "okf::metadata-schema/requirements::concept" in sources
    assert "okf::atomic/57" in sources


def test_read_bundle_index(content_tree) -> None:
    text = okf_content.read_bundle_index()
    assert "okf_version" in text
    assert "metadata-schema" in text
