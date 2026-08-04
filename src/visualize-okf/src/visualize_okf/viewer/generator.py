"""Walk an OKF bundle and emit a self-contained HTML graph visualization.

Derived from GoogleCloudPlatform/knowledge-catalog
okf/src/reference_agent/viewer/generator.py (Apache-2.0).

Bundle parse/walk lives in ``okf_core``; this module adds viz-only coloring
and HTML packaging.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from okf_core.walk import OkfConcept, walk_bundle

# Backward-compatible names for export/tests
Concept = OkfConcept
_walk_concepts = walk_bundle

# Palette tuned for skill-bundles, NIAID Blueprint, and upstream BQ sample types.
_TYPE_PALETTE = {
    "Skill Bundle Example": "#3b82f6",
    "Concept": "#8b5cf6",
    "Daily Digest": "#64748b",
    "Paper": "#10b981",
    "Q&A": "#f59e0b",
    "Tool": "#06b6d4",
    "Publication": "#ec4899",
    "Metrics": "#ef4444",
    "BigQuery Dataset": "#8b5cf6",
    "BigQuery Table": "#3b82f6",
    "Reference": "#10b981",
    "NIAID Blueprint Section": "#3b82f6",
    "NIAID Blueprint Requirements": "#ef4444",
    "Reference Table": "#10b981",
    "Worked Example": "#f59e0b",
    "Document Status": "#64748b",
    "Attested Computation": "#8b5cf6",
}
_DEFAULT_NODE_COLOR = "#94a3b8"
_HASH_PALETTE = (
    "#0ea5e9",
    "#14b8a6",
    "#22c55e",
    "#a855f7",
    "#f97316",
    "#e11d48",
    "#6366f1",
    "#84cc16",
    "#d946ef",
    "#0891b2",
)


def _color_for_type(type_name: str) -> str:
    """Return palette color, or a stable hash color for unknown types."""
    if type_name in _TYPE_PALETTE:
        return _TYPE_PALETTE[type_name]
    if not type_name or type_name == "Unknown":
        return _DEFAULT_NODE_COLOR
    digest = hashlib.sha256(type_name.encode("utf-8")).digest()
    idx = int.from_bytes(digest[:2], "big") % len(_HASH_PALETTE)
    return _HASH_PALETTE[idx]


def concept_to_node(concept: OkfConcept) -> dict[str, Any]:
    color = _color_for_type(concept.type)
    return {
        "data": {
            "id": concept.id,
            "label": concept.title or concept.id,
            "type": concept.type,
            "description": concept.description,
            "resource": concept.resource,
            "tags": concept.tags,
            "color": color,
            "size": 30 + min(60, len(concept.body) // 200),
            "status": concept.status,
            "generated_by": concept.generated_by,
            "generated_at": concept.generated_at,
            "trust_tier": concept.trust_tier,
            "stale_after": concept.stale_after,
            "sources": concept.sources,
        }
    }


def _build_graph(concepts: list[OkfConcept]) -> dict[str, Any]:
    ids = {c.id for c in concepts}
    nodes = [concept_to_node(c) for c in concepts]
    edges: list[dict[str, Any]] = []
    seen_edges: set[tuple[str, str, str]] = set()

    def add_edge(source: str, target: str, kind: str) -> None:
        if target == source or target not in ids:
            return
        key = (source, target, kind)
        if key in seen_edges:
            return
        seen_edges.add(key)
        edges.append(
            {
                "data": {
                    "id": f"{source}__{kind}__{target}",
                    "source": source,
                    "target": target,
                    "kind": kind,
                }
            }
        )

    for c in concepts:
        for target in c.links_to:
            add_edge(c.id, target, "link")
        for target in c.source_links_to:
            add_edge(c.id, target, "source")

    bodies = {c.id: c.body for c in concepts}
    types = sorted({c.type for c in concepts})
    return {
        "nodes": nodes,
        "edges": edges,
        "bodies": bodies,
        "types": types,
        "palette": _TYPE_PALETTE,
    }


def _load_template() -> str:
    template_path = Path(__file__).parent / "templates" / "viz.html"
    return template_path.read_text(encoding="utf-8")


def _load_asset(name: str) -> str:
    asset_path = Path(__file__).parent / "static" / name
    return asset_path.read_text(encoding="utf-8")


def generate_visualization(
    bundle_root: Path,
    out_path: Path,
    *,
    bundle_name: str | None = None,
) -> dict[str, int]:
    """Walk a bundle and write a single self-contained HTML visualization.

    Returns counts: {'concepts': N, 'edges': M, 'bytes': K}.
    """
    bundle_root = Path(bundle_root)
    out_path = Path(out_path)
    if not bundle_root.is_dir():
        raise FileNotFoundError(f"Bundle directory not found: {bundle_root}")

    concepts = walk_bundle(bundle_root)
    graph = _build_graph(concepts)
    template = _load_template()
    css = _load_asset("viz.css")
    js = _load_asset("viz.js")
    name = bundle_name or bundle_root.resolve().name

    html = (
        template.replace("/*__VIZ_CSS__*/", css)
        .replace("/*__VIZ_JS__*/", js)
        .replace("__BUNDLE_NAME__", json.dumps(name))
        .replace("__BUNDLE_DATA__", json.dumps(graph))
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")

    return {
        "concepts": len(concepts),
        "edges": len(graph["edges"]),
        "bytes": len(html.encode("utf-8")),
    }
