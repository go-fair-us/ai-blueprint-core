from __future__ import annotations

import json
import re
from pathlib import Path
from textwrap import dedent

import pytest

from visualize_okf.viewer.generator import (
    _TYPE_PALETTE,
    _color_for_type,
    generate_visualization,
)


def _write(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(body).lstrip(), encoding="utf-8")


def _make_skill_style_bundle(root: Path) -> None:
    """Mini bundle matching skill-bundles conventions (relative links + types)."""
    _write(
        root / "concepts" / "skill-bundle-patterns.md",
        """
        ---
        type: Concept
        title: Skill Bundle Patterns
        description: Core composition patterns.
        tags: [patterns]
        status: stable
        generated: { by: test/fixture, at: 2026-05-28T00:00:00Z }
        ---
        See [example](../examples/nora.md) and absolute [paper](/papers/survey.md).
        """,
    )
    _write(
        root / "examples" / "nora.md",
        """
        ---
        type: Skill Bundle Example
        title: NORA
        description: Night Owl Research Agent.
        tags: [research]
        generated: { by: test/fixture, at: 2026-05-28T00:00:00Z }
        ---
        Related concept: [patterns](../concepts/skill-bundle-patterns.md).
        """,
    )
    _write(
        root / "papers" / "survey.md",
        """
        ---
        type: Paper
        title: Agent Skills Survey
        description: Survey paper note.
        generated: { by: test/fixture, at: 2026-05-28T00:00:00Z }
        ---
        Standalone paper note.
        """,
    )
    _write(
        root / "skill-bundles.md",
        """
        ---
        type: Publication
        title: Skill Bundles Catalog
        description: Living catalog.
        ---
        Catalog entry for [NORA](examples/nora.md).
        """,
    )
    # Reserved files — must not become nodes
    _write(root / "index.md", "# Bundle\n* [concepts](concepts/)\n")
    _write(
        root / "log.md",
        """
        # Directory Update Log

        ## 2026-05-28
        * **Creation**: Established bundle.
        """,
    )


def _make_bq_style_bundle(root: Path) -> None:
    """Upstream-style relative links for regression."""
    _write(
        root / "datasets" / "my_dataset.md",
        """
        ---
        type: BigQuery Dataset
        title: My dataset
        description: A test dataset.
        resource: https://example.com/dataset
        tags: [test]
        generated: { by: test/fixture, at: 2026-05-28T00:00:00Z }
        ---
        Parent dataset for [users](../tables/users.md).
        """,
    )
    _write(
        root / "tables" / "users.md",
        """
        ---
        type: BigQuery Table
        title: Users
        description: User profiles.
        resource: https://example.com/users
        tags: [users]
        generated: { by: test/fixture, at: 2026-05-28T00:00:00Z }
        ---
        Joinable with [events](events.md).
        """,
    )
    _write(
        root / "tables" / "events.md",
        """
        ---
        type: BigQuery Table
        title: Events
        description: User events.
        resource: https://example.com/events
        tags: [events]
        generated: { by: test/fixture, at: 2026-05-28T00:00:00Z }
        ---
        See [users](users.md).
        """,
    )
    _write(root / "index.md", "# My Bundle\n")


def _make_v02_provenance_bundle(root: Path) -> None:
    """v0.2 fields + provenance edge from sources[].resource to in-bundle concept."""
    _write(
        root / "policy" / "revenue.md",
        """
        ---
        type: Reference
        title: Revenue policy
        description: Canonical policy note.
        status: stable
        generated: { by: human:alice, at: 2026-06-01T00:00:00Z }
        verified: { by: human:alice, at: 2026-06-02T00:00:00Z }
        ---
        Policy body.
        """,
    )
    _write(
        root / "metrics" / "revenue.md",
        """
        ---
        type: Metrics
        title: Revenue metric
        description: Derived figure.
        status: draft
        generated: { by: agent/gepa, at: 2026-06-10T12:00:00Z }
        verified: { by: process:nightly, at: 2026-06-11T02:00:00Z }
        stale_after: 2026-12-31
        sources:
          - id: rev-policy
            resource: /policy/revenue.md
            title: Revenue policy
          - id: external
            resource: https://example.com/handbook
            title: External handbook
        ---
        See also prose link to [policy](/policy/revenue.md).
        """,
    )
    # Legacy timestamp only (v0.1 fallback)
    _write(
        root / "legacy.md",
        """
        ---
        type: Concept
        title: Legacy note
        description: Still on timestamp.
        timestamp: '2026-05-28T00:00:00+00:00'
        ---
        Old shape.
        """,
    )
    _write(
        root / "index.md",
        """
        ---
        okf_version: "0.2"
        ---

        # Bundle
        """,
    )


def _extract_bundle_data(html: str) -> dict:
    m = re.search(r"window\.BUNDLE\s*=\s*(\{.*?\});", html, re.DOTALL)
    assert m, "BUNDLE JSON not found in generated HTML"
    return json.loads(m.group(1))


def test_generate_visualization_writes_html(tmp_path: Path):
    bundle = tmp_path / "bundle"
    _make_skill_style_bundle(bundle)
    out = tmp_path / "viz.html"
    stats = generate_visualization(bundle, out, bundle_name="Skill Bundles OKF")

    assert out.exists()
    assert stats["concepts"] == 4
    assert stats["edges"] >= 3
    assert stats["bytes"] > 0
    html = out.read_text(encoding="utf-8")
    assert "<title>OKF Bundle Viewer</title>" in html
    assert "cytoscape" in html.lower()
    assert "marked" in html.lower()
    assert '"Skill Bundles OKF"' in html
    assert "detail-sources" in html
    assert "OKF v0.2 bundle" in html


def test_reserved_files_are_not_concepts(tmp_path: Path):
    bundle = tmp_path / "bundle"
    _make_skill_style_bundle(bundle)
    out = tmp_path / "viz.html"
    generate_visualization(bundle, out)
    data = _extract_bundle_data(out.read_text(encoding="utf-8"))
    ids = {n["data"]["id"] for n in data["nodes"]}
    assert "index" not in ids
    assert "log" not in ids
    assert ids == {
        "concepts/skill-bundle-patterns",
        "examples/nora",
        "papers/survey",
        "skill-bundles",
    }


def test_relative_and_absolute_links_become_edges(tmp_path: Path):
    bundle = tmp_path / "bundle"
    _make_skill_style_bundle(bundle)
    out = tmp_path / "viz.html"
    generate_visualization(bundle, out)
    data = _extract_bundle_data(out.read_text(encoding="utf-8"))
    pairs = {
        (e["data"]["source"], e["data"]["target"], e["data"].get("kind", "link"))
        for e in data["edges"]
    }
    assert ("concepts/skill-bundle-patterns", "examples/nora", "link") in pairs
    assert ("concepts/skill-bundle-patterns", "papers/survey", "link") in pairs
    assert ("examples/nora", "concepts/skill-bundle-patterns", "link") in pairs
    assert ("skill-bundles", "examples/nora", "link") in pairs


def test_bq_style_relative_links(tmp_path: Path):
    bundle = tmp_path / "bundle"
    _make_bq_style_bundle(bundle)
    out = tmp_path / "viz.html"
    stats = generate_visualization(bundle, out)
    assert stats["concepts"] == 3
    data = _extract_bundle_data(out.read_text(encoding="utf-8"))
    pairs = {(e["data"]["source"], e["data"]["target"]) for e in data["edges"]}
    assert ("datasets/my_dataset", "tables/users") in pairs
    assert ("tables/users", "tables/events") in pairs
    assert ("tables/events", "tables/users") in pairs


def test_missing_link_targets_are_skipped(tmp_path: Path):
    bundle = tmp_path / "bundle"
    _write(
        bundle / "examples" / "lonely.md",
        """
        ---
        type: Skill Bundle Example
        title: Lonely
        description: Has a dangling link.
        generated: { by: test/fixture, at: 2026-05-28T00:00:00Z }
        ---
        Links to [missing](missing.md).
        """,
    )
    out = tmp_path / "viz.html"
    generate_visualization(bundle, out)
    data = _extract_bundle_data(out.read_text(encoding="utf-8"))
    assert data["edges"] == []
    assert len(data["nodes"]) == 1


def test_node_colors_match_skill_palette(tmp_path: Path):
    bundle = tmp_path / "bundle"
    _make_skill_style_bundle(bundle)
    out = tmp_path / "viz.html"
    generate_visualization(bundle, out)
    data = _extract_bundle_data(out.read_text(encoding="utf-8"))
    by_id = {n["data"]["id"]: n["data"] for n in data["nodes"]}
    assert by_id["concepts/skill-bundle-patterns"]["color"] == "#8b5cf6"
    assert by_id["examples/nora"]["color"] == "#3b82f6"
    assert by_id["papers/survey"]["color"] == "#10b981"
    assert by_id["skill-bundles"]["color"] == "#ec4899"


def test_niaid_palette_and_hash_fallback():
    assert _color_for_type("NIAID Blueprint Requirements") == _TYPE_PALETTE[
        "NIAID Blueprint Requirements"
    ]
    assert _color_for_type("NIAID Blueprint Section") == "#3b82f6"
    assert _color_for_type("Worked Example") == "#f59e0b"
    # Unknown types: stable hash color (not the default slate)
    a = _color_for_type("Completely Novel Type XYZ")
    b = _color_for_type("Completely Novel Type XYZ")
    assert a == b
    assert a.startswith("#")
    assert a != _color_for_type("Another Totally Different Type")


def test_v02_fields_projected_on_nodes(tmp_path: Path):
    bundle = tmp_path / "bundle"
    _make_v02_provenance_bundle(bundle)
    out = tmp_path / "viz.html"
    generate_visualization(bundle, out)
    data = _extract_bundle_data(out.read_text(encoding="utf-8"))
    by_id = {n["data"]["id"]: n["data"] for n in data["nodes"]}

    metric = by_id["metrics/revenue"]
    assert metric["status"] == "draft"
    assert metric["generated_by"] == "agent/gepa"
    assert metric["generated_at"] == "2026-06-10T12:00:00Z"
    assert metric["trust_tier"] == "machine-confirmed"
    assert metric["stale_after"] == "2026-12-31"
    assert len(metric["sources"]) == 2
    assert metric["sources"][0]["id"] == "rev-policy"

    policy = by_id["policy/revenue"]
    assert policy["trust_tier"] == "human-reviewed"

    legacy = by_id["legacy"]
    assert legacy["generated_at"] == "2026-05-28T00:00:00+00:00"
    assert legacy["generated_by"] == ""
    assert legacy["trust_tier"] == "unverified"
    assert legacy["status"] == "stable"


def test_provenance_source_edges(tmp_path: Path):
    bundle = tmp_path / "bundle"
    _make_v02_provenance_bundle(bundle)
    out = tmp_path / "viz.html"
    generate_visualization(bundle, out)
    data = _extract_bundle_data(out.read_text(encoding="utf-8"))
    edges = data["edges"]
    by_kind = {}
    for e in edges:
        d = e["data"]
        by_kind.setdefault(d.get("kind", "link"), set()).add(
            (d["source"], d["target"])
        )
    assert ("metrics/revenue", "policy/revenue") in by_kind.get("source", set())
    # Prose markdown link still creates a link edge
    assert ("metrics/revenue", "policy/revenue") in by_kind.get("link", set())
    # External handbook must not create an edge
    all_targets = {e["data"]["target"] for e in edges}
    assert "https://example.com/handbook" not in all_targets


def test_raises_when_bundle_missing(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        generate_visualization(tmp_path / "nope", tmp_path / "viz.html")


def test_niaid_blueprint_bundle_if_present():
    """Integration: real repo bundle when checked out beside this package."""
    repo_bundle = (
        Path(__file__).resolve().parents[3]
        / "okf"
        / "bundles"
        / "niaid_blueprint"
    )
    if not repo_bundle.is_dir():
        pytest.skip("niaid_blueprint bundle not present")
    out = Path("/tmp") / "niaid_blueprint_viz_test.html"
    stats = generate_visualization(
        repo_bundle, out, bundle_name="NIAID Blueprint"
    )
    assert stats["concepts"] == 27
    assert stats["edges"] >= 30
    data = _extract_bundle_data(out.read_text(encoding="utf-8"))
    sample = next(n["data"] for n in data["nodes"] if n["data"]["id"] == "overview/background")
    assert sample["generated_by"]
    assert sample["sources"]
    assert sample["status"] == "stable"
    assert sample["color"] == _TYPE_PALETTE["NIAID Blueprint Section"]
