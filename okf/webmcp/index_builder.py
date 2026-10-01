"""Build a JSON tree and search index from an OKF v0.2 bundle.

Uses ``okf_core.walk_bundle`` for typed concepts and a filesystem walk for
``index.md`` / ``log.md`` (reserved names that the walker skips).
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

WEB_ROOT = Path(__file__).resolve().parent
OKF_ROOT = WEB_ROOT.parent
REPO_ROOT = OKF_ROOT.parent
DEFAULT_BUNDLE = OKF_ROOT / "bundles" / "niaid_blueprint"

_OKF_CORE_SRC = REPO_ROOT / "src" / "okf_core" / "src"
if _OKF_CORE_SRC.is_dir() and str(_OKF_CORE_SRC) not in sys.path:
    sys.path.insert(0, str(_OKF_CORE_SRC))

from okf_core import OKFDocument, walk_bundle  # noqa: E402

# FAIR / Blueprint pillars — keys match mcp_bp.okf_content.
PILLAR_PREFIXES: dict[str, str] = {
    "metadata": "metadata-schema",
    "identifiers": "persistent-identifiers",
    "api": "api-specification",
    "citation": "citation",
    "outreach": "outreach-training",
}

_HEADING_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)
_ATOMIC_SPLIT = "# Atomic concepts"


class BundlePathError(ValueError):
    """Raised when a requested path is missing or escapes the bundle root."""


def pillar_for_id(concept_id: str) -> str | None:
    """Return the FAIR pillar key for a concept id, if any."""
    cid = concept_id.strip().lstrip("/")
    for key, prefix in PILLAR_PREFIXES.items():
        if cid == prefix or cid.startswith(prefix + "/"):
            return key
    return None


def heading_title(body: str, fallback: str) -> str:
    """First ATX h1 in body, or ``fallback``."""
    if not body:
        return fallback
    m = _HEADING_RE.search(body)
    return m.group(1).strip() if m else fallback


def prose_body(body: str) -> str:
    """Body text above the Atomic concepts table, if present."""
    if not body:
        return ""
    if _ATOMIC_SPLIT in body:
        return body.split(_ATOMIC_SPLIT, 1)[0].strip()
    return body.strip()


def resolve_bundle_file(bundle_root: Path, rel: str) -> Path:
    """Resolve ``rel`` to a Markdown file inside ``bundle_root``.

    Rejects empty paths, URLs, and any resolution that escapes the bundle.
    """
    if rel is None:
        raise BundlePathError("Missing path")
    text = str(rel).strip().lstrip("/")
    if not text:
        raise BundlePathError("Empty path")
    if "://" in text:
        raise BundlePathError(f"URL paths are not allowed: {rel!r}")
    # Normalize separators; still reject ".." before resolve as a fast path.
    parts = Path(text).parts
    if any(p in ("..", "") for p in parts):
        raise BundlePathError(f"Path escapes bundle: {rel!r}")

    root = bundle_root.resolve()
    candidate = (root / text).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise BundlePathError(f"Path escapes bundle: {rel!r}") from exc
    if not candidate.is_file():
        raise BundlePathError(f"Not a file: {rel!r}")
    if candidate.suffix.lower() != ".md":
        raise BundlePathError(f"Not a Markdown file: {rel!r}")
    return candidate


def _atomic_dict(a: Any) -> dict[str, Any]:
    return {
        "number": a.number,
        "text": a.text,
        "source_lines": a.source_lines,
        "parent_id": a.parent_id,
        "concept_id": a.concept_id,
    }


def _file_id(rel_posix: str) -> str:
    if rel_posix.endswith(".md"):
        return rel_posix[:-3]
    return rel_posix


def _kind_for_name(name: str, is_concept: bool) -> str:
    if is_concept:
        return "concept"
    if name == "index.md":
        return "index"
    if name == "log.md":
        return "log"
    return "file"


def _concept_document(c: Any, linked_from: list[dict[str, str]]) -> dict[str, Any]:
    path = c.id + ".md"
    return {
        "id": c.id,
        "kind": "concept",
        "path": path,
        "title": c.title,
        "description": c.description,
        "type": c.type,
        "tags": list(c.tags),
        "status": c.status,
        "normative": c.normative,
        "section": c.section,
        "source_lines": c.source_lines,
        "concept_range": c.concept_range,
        "pillar": pillar_for_id(c.id),
        "prefix": c.id.split("/", 1)[0] if "/" in c.id else c.id,
        "resource": c.resource,
        "sources": list(c.sources),
        "trust_tier": c.trust_tier,
        "generated_by": c.generated_by,
        "generated_at": c.generated_at,
        "stale_after": c.stale_after,
        "source_document": c.source_document,
        "links_to": list(c.links_to),
        "linked_from": linked_from,
        "atomics": [_atomic_dict(a) for a in c.atomics],
        "body": c.body,
        "prose": prose_body(c.body),
    }


def _reserved_document(md_path: Path, bundle_root: Path) -> dict[str, Any]:
    rel = md_path.relative_to(bundle_root).as_posix()
    cid = _file_id(rel)
    text = md_path.read_text(encoding="utf-8", errors="replace")
    parsed = OKFDocument.parse(text)
    fm = parsed.frontmatter or {}
    kind = _kind_for_name(md_path.name, is_concept=False)
    title = str(fm.get("title") or "") or heading_title(parsed.body, cid)
    prefix = cid.split("/", 1)[0] if "/" in cid else cid
    return {
        "id": cid,
        "kind": kind,
        "path": rel,
        "title": title,
        "description": str(fm.get("description") or ""),
        "type": str(fm.get("type") or ""),
        "tags": [],
        "status": str(fm.get("status") or ""),
        "normative": None,
        "section": "",
        "source_lines": "",
        "concept_range": "",
        "pillar": pillar_for_id(cid),
        "prefix": prefix,
        "resource": str(fm.get("resource") or ""),
        "sources": [],
        "trust_tier": "",
        "generated_by": "",
        "generated_at": "",
        "stale_after": "",
        "source_document": "",
        "links_to": [],
        "linked_from": [],
        "atomics": [],
        "body": parsed.body,
        "prose": parsed.body.strip(),
        "okf_version": str(fm["okf_version"]) if fm.get("okf_version") is not None else "",
    }


def build_documents(bundle_root: Path) -> list[dict[str, Any]]:
    """All Markdown documents in the bundle (concepts + index/log files)."""
    bundle_root = bundle_root.resolve()
    concepts = walk_bundle(bundle_root)
    by_id = {c.id: c for c in concepts}

    inbound: dict[str, list[str]] = defaultdict(list)
    for c in concepts:
        for target in c.links_to:
            inbound[target].append(c.id)

    def _link_summaries(ids: list[str]) -> list[dict[str, str]]:
        out: list[dict[str, str]] = []
        for cid in ids:
            other = by_id.get(cid)
            out.append({"id": cid, "title": other.title if other else cid})
        return out

    documents: list[dict[str, Any]] = []
    seen: set[str] = set()
    for md_path in sorted(bundle_root.rglob("*.md")):
        rel = md_path.relative_to(bundle_root).as_posix()
        cid = _file_id(rel)
        seen.add(cid)
        if cid in by_id:
            c = by_id[cid]
            documents.append(_concept_document(c, _link_summaries(inbound.get(cid, []))))
        else:
            documents.append(_reserved_document(md_path, bundle_root))

    # Concepts whose files were skipped by rglob should not happen; keep a guard.
    for c in concepts:
        if c.id not in seen:
            documents.append(_concept_document(c, _link_summaries(inbound.get(c.id, []))))
    return documents


def build_tree(bundle_root: Path, documents: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Nested directory tree of Markdown files."""
    bundle_root = bundle_root.resolve()
    by_id = {d["id"]: d for d in (documents or [])}

    def dir_node(path: Path) -> dict[str, Any]:
        rel = "" if path == bundle_root else path.relative_to(bundle_root).as_posix()
        children: list[dict[str, Any]] = []
        entries = [
            e
            for e in path.iterdir()
            if not e.name.startswith(".") and (e.is_dir() or e.suffix.lower() == ".md")
        ]
        entries.sort(key=lambda e: (not e.is_dir(), e.name.lower()))
        for entry in entries:
            if entry.is_dir():
                child = dir_node(entry)
                if child["children"]:
                    children.append(child)
                continue
            cid = _file_id(entry.relative_to(bundle_root).as_posix())
            doc = by_id.get(cid, {})
            children.append(
                {
                    "name": entry.name,
                    "kind": doc.get("kind") or _kind_for_name(entry.name, False),
                    "id": cid,
                    "title": doc.get("title") or entry.stem,
                }
            )
        return {
            "name": path.name,
            "kind": "dir",
            "id": rel,
            "children": children,
        }

    return dir_node(bundle_root)


def build_payload(bundle_root: Path | None = None) -> dict[str, Any]:
    """Combined index + tree payload for ``/data/index.json``."""
    root = (bundle_root or DEFAULT_BUNDLE).resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"Bundle directory not found: {root}")

    documents = build_documents(root)
    tree = build_tree(root, documents)
    concepts = [d for d in documents if d["kind"] == "concept"]
    atomics = [a for d in concepts for a in d["atomics"]]
    types = sorted({d["type"] for d in concepts if d.get("type")})
    tags = sorted({t for d in concepts for t in (d.get("tags") or [])})
    okf_version = ""
    root_index = next((d for d in documents if d["id"] == "index"), None)
    if root_index:
        okf_version = str(root_index.get("okf_version") or "")

    return {
        "bundle": root.name,
        "okf_version": okf_version,
        "stats": {
            "concepts": len(concepts),
            "atomics": len(atomics),
            "documents": len(documents),
            "types": len(types),
            "tags": len(tags),
        },
        "pillars": dict(PILLAR_PREFIXES),
        "types": types,
        "tags": tags,
        "documents": documents,
        "tree": tree,
    }
