"""Unit tests for OKF document helpers (v0.2 provenance / trust / lifecycle)."""

from __future__ import annotations

from textwrap import dedent

import pytest

from visualize_okf.document import (
    OKFDocument,
    OKFDocumentError,
    content_timestamp,
    generated_by,
    lifecycle_status,
    normalize_sources,
    trust_tier,
)


def test_validate_requires_only_type():
    doc = OKFDocument.parse(
        dedent(
            """
            ---
            type: Concept
            ---
            Body.
            """
        ).lstrip()
    )
    doc.validate()  # does not raise


def test_validate_rejects_missing_type():
    doc = OKFDocument.parse(
        dedent(
            """
            ---
            title: No type
            ---
            Body.
            """
        ).lstrip()
    )
    with pytest.raises(OKFDocumentError, match="type"):
        doc.validate()


def test_content_timestamp_prefers_generated_at():
    fm = {
        "generated": {"by": "agent/1", "at": "2026-08-03T12:00:00Z"},
        "timestamp": "2020-01-01T00:00:00Z",
    }
    assert content_timestamp(fm) == "2026-08-03T12:00:00Z"
    assert generated_by(fm) == "agent/1"


def test_content_timestamp_falls_back_to_legacy_timestamp():
    fm = {"timestamp": "2026-05-28T00:00:00+00:00"}
    assert content_timestamp(fm) == "2026-05-28T00:00:00+00:00"
    assert generated_by(fm) is None


def test_trust_tier_unverified():
    assert trust_tier({}) == "unverified"
    assert trust_tier({"verified": []}) == "unverified"


def test_trust_tier_machine_confirmed():
    fm = {"verified": {"by": "process:nightly", "at": "2026-06-01T00:00:00Z"}}
    assert trust_tier(fm) == "machine-confirmed"
    fm_list = {
        "verified": [
            {"by": "agent/x", "at": "2026-06-01T00:00:00Z"},
            {"by": "process:y", "at": "2026-06-02T00:00:00Z"},
        ]
    }
    assert trust_tier(fm_list) == "machine-confirmed"


def test_trust_tier_human_reviewed():
    fm = {
        "verified": [
            {"by": "process:nightly", "at": "2026-06-01T00:00:00Z"},
            {"by": "human:alice", "at": "2026-06-02T00:00:00Z"},
        ]
    }
    assert trust_tier(fm) == "human-reviewed"


def test_lifecycle_status_default_stable():
    assert lifecycle_status({}) == "stable"
    assert lifecycle_status({"status": "draft"}) == "draft"


def test_normalize_sources():
    fm = {
        "sources": [
            {
                "id": "bp",
                "resource": "https://example.com/doc.md",
                "title": "Doc",
                "author": "process:pub",
            },
            {"resource": ""},  # dropped
            "not-a-dict",  # dropped
            {"resource": "/other/concept.md", "id": "local"},
        ]
    }
    src = normalize_sources(fm)
    assert len(src) == 2
    assert src[0]["id"] == "bp"
    assert src[0]["author"] == "process:pub"
    assert src[1]["resource"] == "/other/concept.md"
