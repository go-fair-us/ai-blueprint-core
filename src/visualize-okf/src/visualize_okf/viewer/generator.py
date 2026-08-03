"""Walk an OKF bundle and emit a self-contained HTML graph visualization.

Derived from GoogleCloudPlatform/knowledge-catalog
okf/src/reference_agent/viewer/generator.py (Apache-2.0).

Local changes:
  - Expanded type palette for skill-bundles, NIAID Blueprint, and generic OKF
  - Stable hash-color fallback for unknown types
  - Skip reserved files index.md and log.md
  - Resolve absolute bundle-root links (/path.md) as graph edges (OKF §6)
  - Project OKF v0.2 trust/provenance/lifecycle fields onto nodes
  - Provenance edges when sources[].resource points at an in-bundle concept
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from visualize_okf.document import (
    OKFDocument,
    OKFDocumentError,
    _as_iso_str,
    content_timestamp,
    generated_by,
    lifecycle_status,
    normalize_sources,
    trust_tier,
)

_RESERVED_NAMES = frozenset({"index.md", "log.md"})
_LINK_RE = re.compile(r"\]\(([^)\s]+\.md)(?:#[A-Za-z0-9_\-]*)?\)")

# Palette tuned for skill-bundles, NIAID Blueprint, and upstream BQ sample types.
# Unknown types get a stable hash color (see _color_for_type).
_TYPE_PALETTE = {
    # skill-bundles / hermes wiki types
    "Skill Bundle Example": "#3b82f6",  # blue
    "Concept": "#8b5cf6",  # purple
    "Daily Digest": "#64748b",  # slate
    "Paper": "#10b981",  # green
    "Q&A": "#f59e0b",  # amber
    "Tool": "#06b6d4",  # cyan
    "Publication": "#ec4899",  # pink
    "Metrics": "#ef4444",  # red
    # upstream BQ sample types (still supported)
    "BigQuery Dataset": "#8b5cf6",
    "BigQuery Table": "#3b82f6",
    "Reference": "#10b981",
    # NIAID Blueprint OKF types
    "NIAID Blueprint Section": "#3b82f6",  # blue
    "NIAID Blueprint Requirements": "#ef4444",  # red
    "Reference Table": "#10b981",  # green
    "Worked Example": "#f59e0b",  # amber
    "Document Status": "#64748b",  # slate
    # OKF v0.2 computation type
    "Attested Computation": "#8b5cf6",  # purple
}
# Fallback when type is missing/empty after hashing is not applicable
_DEFAULT_NODE_COLOR = "#94a3b8"

# Distinct hues for stable hash of unknown types (readable on white)
_HASH_PALETTE = (
    "#0ea5e9",  # sky
    "#14b8a6",  # teal
    "#22c55e",  # green
    "#a855f7",  # purple
    "#f97316",  # orange
    "#e11d48",  # rose
    "#6366f1",  # indigo
    "#84cc16",  # lime
    "#d946ef",  # fuchsia
    "#0891b2",  # cyan-dark
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


@dataclass
class Concept:
    id: str
    type: str
    title: str
    description: str
    resource: str
    tags: list[str]
    body: str
    links_to: list[str] = field(default_factory=list)
    # OKF v0.2 trust / lifecycle / provenance
    status: str = "stable"
    generated_by: str = ""
    generated_at: str = ""
    trust_tier: str = "unverified"
    stale_after: str = ""
    sources: list[dict[str, str]] = field(default_factory=list)
    source_links_to: list[str] = field(default_factory=list)

    def to_node(self) -> dict[str, Any]:
        color = _color_for_type(self.type)
        return {
            "data": {
                "id": self.id,
                "label": self.title or self.id,
                "type": self.type,
                "description": self.description,
                "resource": self.resource,
                "tags": self.tags,
                "color": color,
                "size": 30 + min(60, len(self.body) // 200),
                "status": self.status,
                "generated_by": self.generated_by,
                "generated_at": self.generated_at,
                "trust_tier": self.trust_tier,
                "stale_after": self.stale_after,
                "sources": self.sources,
            }
        }


def _resolve_md_target(
    target: str, doc_dir: Path, bundle_root: Path
) -> str | None:
    """Resolve a .md path (relative or absolute-from-bundle-root) to a concept id.

    Returns None if the path escapes the bundle or is not resolvable.
    """
    if not target or "://" in target:
        return None
    path = target.split("#")[0].split("?")[0]
    if not path:
        return None
    bundle_root_resolved = bundle_root.resolve()
    try:
        if path.startswith("/"):
            # Absolute-from-bundle-root (OKF §6)
            resolved = (bundle_root / path.lstrip("/")).resolve().relative_to(
                bundle_root_resolved
            )
        else:
            resolved = (doc_dir / path).resolve().relative_to(bundle_root_resolved)
    except ValueError:
        return None
    rel = resolved.as_posix()
    if rel.endswith(".md"):
        rel = rel[:-3]
    return rel or None


def _extract_links(body: str, doc_dir: Path, bundle_root: Path) -> list[str]:
    """Resolve internal .md links (relative or absolute-from-bundle-root) to concept ids."""
    out: list[str] = []
    seen: set[str] = set()
    for m in _LINK_RE.finditer(body):
        rel = _resolve_md_target(m.group(1), doc_dir, bundle_root)
        if rel and rel not in seen:
            seen.add(rel)
            out.append(rel)
    return out


def _resource_to_concept_id(
    resource: str, doc_dir: Path, bundle_root: Path, concept_ids: set[str]
) -> str | None:
    """Map a sources[].resource value to an in-bundle concept id when possible.

    Accepts absolute URLs (ignored), bundle-absolute paths (/foo.md or /foo),
    relative paths, and bare concept ids already present in the bundle.
    """
    if not resource or not str(resource).strip():
        return None
    res = str(resource).strip()
    if "://" in res:
        return None

    # Already a concept id (no .md)
    if res in concept_ids:
        return res
    bare = res[1:] if res.startswith("/") else res
    if bare.endswith(".md"):
        bare = bare[:-3]
    if bare in concept_ids:
        return bare

    # Path-style: ensure .md for resolver when it looks like a file path
    path = res
    if not path.endswith(".md") and ("/" in path or path.startswith(".")):
        path = path + ".md"
    elif not path.endswith(".md") and path.startswith("/"):
        path = path + ".md"

    if path.endswith(".md") or path.startswith("/") or path.startswith("."):
        cid = _resolve_md_target(
            path if path.endswith(".md") else path + ".md",
            doc_dir,
            bundle_root,
        )
        if cid and cid in concept_ids:
            return cid
    return None


def _source_concept_ids(
    sources: list[dict[str, str]],
    doc_dir: Path,
    bundle_root: Path,
    concept_ids: set[str],
) -> list[str]:
    """Collect unique in-bundle concept ids referenced by sources[].resource."""
    out: list[str] = []
    seen: set[str] = set()
    for entry in sources:
        resource = entry.get("resource") or ""
        cid = _resource_to_concept_id(resource, doc_dir, bundle_root, concept_ids)
        if cid and cid not in seen:
            seen.add(cid)
            out.append(cid)
    return out


def _walk_concepts(bundle_root: Path) -> list[Concept]:
    concepts: list[Concept] = []
    # First pass: parse all concepts (source edges resolved in second pass)
    pending: list[tuple[Concept, Path]] = []
    for md_path in sorted(bundle_root.rglob("*.md")):
        if md_path.name in _RESERVED_NAMES:
            continue
        rel = md_path.relative_to(bundle_root).with_suffix("")
        concept_id = "/".join(rel.parts)
        try:
            doc = OKFDocument.parse(md_path.read_text(encoding="utf-8"))
        except OKFDocumentError:
            continue
        # Skip docs with no frontmatter type (e.g. stray helper files)
        fm = doc.frontmatter or {}
        if not fm.get("type"):
            continue
        tags = fm.get("tags") or []
        if not isinstance(tags, list):
            tags = [str(tags)]
        sources = normalize_sources(fm)
        gen_at = content_timestamp(fm) or ""
        gen_by = generated_by(fm) or ""
        stale = _as_iso_str(fm.get("stale_after")) or ""
        concept = Concept(
            id=concept_id,
            type=str(fm.get("type") or "Unknown"),
            title=str(fm.get("title") or concept_id),
            description=str(fm.get("description") or ""),
            resource=str(fm.get("resource") or ""),
            tags=[str(t) for t in tags],
            body=doc.body or "",
            links_to=_extract_links(doc.body or "", md_path.parent, bundle_root),
            status=lifecycle_status(fm),
            generated_by=gen_by,
            generated_at=gen_at,
            trust_tier=trust_tier(fm),
            stale_after=stale,
            sources=sources,
        )
        pending.append((concept, md_path.parent))
        concepts.append(concept)

    # Second pass: resolve provenance edges now that all concept ids are known
    concept_ids = {c.id for c in concepts}
    for concept, doc_dir in pending:
        concept.source_links_to = _source_concept_ids(
            concept.sources, doc_dir, bundle_root, concept_ids
        )
    return concepts


def _build_graph(concepts: list[Concept]) -> dict[str, Any]:
    ids = {c.id for c in concepts}
    nodes = [c.to_node() for c in concepts]
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

    concepts = _walk_concepts(bundle_root)
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
