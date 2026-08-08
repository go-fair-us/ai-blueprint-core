"""Tests for hybrid search over OKF chunks."""

from __future__ import annotations

from mcp_bp import hybrid_search


def test_okf_collection_finds_atomic(content_tree) -> None:
    hits = hybrid_search.hybrid_search("identifier DOI", collection="okf")
    assert hits
    assert all(h.source == "okf" for h in hits)
    # Prefer an atomic or concept that mentions DOI
    paths = " ".join(h.path for h in hits)
    titles = " ".join(h.section_title for h in hits)
    excerpts = " ".join(h.excerpt for h in hits)
    blob = paths + titles + excerpts
    assert "DOI" in blob or "identifier" in blob.lower() or "atomic" in blob


def test_default_search_excludes_okf(content_tree) -> None:
    """Unscoped search remains docs+prompts so existing clients keep ranking."""
    hits = hybrid_search.hybrid_search("identifier DOI")
    assert all(h.source in ("docs", "prompts") for h in hits)


def test_docs_collection_unchanged(content_tree) -> None:
    hits = hybrid_search.hybrid_search("JSON-LD", collection="docs")
    assert hits
    assert all(h.source == "docs" for h in hits)
