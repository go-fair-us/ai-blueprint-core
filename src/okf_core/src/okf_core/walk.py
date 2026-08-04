"""Walk an OKF bundle and produce structured concept records.

Shared by visualize-okf, okf2rdf, and other consumers. Link resolution
follows OKF §6 (relative and absolute-from-bundle-root ``/path.md`` links).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from okf_core.atomic import AtomicConcept, parse_atomic_concepts
from okf_core.document import (
    OKFDocument,
    OKFDocumentError,
    _as_iso_str,
    content_timestamp,
    generated_by,
    lifecycle_status,
    normalize_sources,
    trust_tier,
)

RESERVED_NAMES = frozenset({"index.md", "log.md"})
_LINK_RE = re.compile(r"\]\(([^)\s]+\.md)(?:#[A-Za-z0-9_\-]*)?\)")


@dataclass
class OkfConcept:
    """One OKF concept document (path id = path without ``.md``)."""

    id: str
    type: str
    title: str
    description: str
    resource: str
    tags: list[str]
    body: str
    links_to: list[str] = field(default_factory=list)
    status: str = "stable"
    generated_by: str = ""
    generated_at: str = ""
    trust_tier: str = "unverified"
    stale_after: str = ""
    sources: list[dict[str, str]] = field(default_factory=list)
    source_links_to: list[str] = field(default_factory=list)
    # Common producer extensions (NIAID Blueprint bundle and similar)
    source_document: str = ""
    source_lines: str = ""
    section: str = ""
    normative: bool | None = None
    concept_range: str = ""
    # Full frontmatter for unmapped extensions
    frontmatter: dict[str, Any] = field(default_factory=dict)
    # Rows from body ``# Atomic concepts`` table
    atomics: list[AtomicConcept] = field(default_factory=list)


def resolve_md_target(
    target: str, doc_dir: Path, bundle_root: Path
) -> str | None:
    """Resolve a .md path to a concept id, or None if outside the bundle."""
    if not target or "://" in target:
        return None
    path = target.split("#")[0].split("?")[0]
    if not path:
        return None
    bundle_root_resolved = bundle_root.resolve()
    try:
        if path.startswith("/"):
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


def extract_links(body: str, doc_dir: Path, bundle_root: Path) -> list[str]:
    """Resolve internal .md links in body text to concept ids."""
    out: list[str] = []
    seen: set[str] = set()
    for m in _LINK_RE.finditer(body):
        rel = resolve_md_target(m.group(1), doc_dir, bundle_root)
        if rel and rel not in seen:
            seen.add(rel)
            out.append(rel)
    return out


def resource_to_concept_id(
    resource: str, doc_dir: Path, bundle_root: Path, concept_ids: set[str]
) -> str | None:
    """Map a sources[].resource value to an in-bundle concept id when possible."""
    if not resource or not str(resource).strip():
        return None
    res = str(resource).strip()
    if "://" in res:
        return None

    if res in concept_ids:
        return res
    bare = res[1:] if res.startswith("/") else res
    if bare.endswith(".md"):
        bare = bare[:-3]
    if bare in concept_ids:
        return bare

    path = res
    if not path.endswith(".md") and ("/" in path or path.startswith(".")):
        path = path + ".md"
    elif not path.endswith(".md") and path.startswith("/"):
        path = path + ".md"

    if path.endswith(".md") or path.startswith("/") or path.startswith("."):
        cid = resolve_md_target(
            path if path.endswith(".md") else path + ".md",
            doc_dir,
            bundle_root,
        )
        if cid and cid in concept_ids:
            return cid
    return None


def source_concept_ids(
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
        cid = resource_to_concept_id(resource, doc_dir, bundle_root, concept_ids)
        if cid and cid not in seen:
            seen.add(cid)
            out.append(cid)
    return out


def _normative_value(raw: Any) -> bool | None:
    if raw is None:
        return None
    if isinstance(raw, bool):
        return raw
    text = str(raw).strip().lower()
    if text in ("true", "yes", "1"):
        return True
    if text in ("false", "no", "0"):
        return False
    return None


def walk_bundle(bundle_root: Path) -> list[OkfConcept]:
    """Walk a bundle directory and return all typed concept documents.

    Skips reserved ``index.md`` and ``log.md``. Documents without a non-empty
    ``type`` frontmatter field are skipped.
    """
    bundle_root = Path(bundle_root)
    if not bundle_root.is_dir():
        raise FileNotFoundError(f"Bundle directory not found: {bundle_root}")

    concepts: list[OkfConcept] = []
    pending: list[tuple[OkfConcept, Path]] = []

    for md_path in sorted(bundle_root.rglob("*.md")):
        if md_path.name in RESERVED_NAMES:
            continue
        rel = md_path.relative_to(bundle_root).with_suffix("")
        concept_id = "/".join(rel.parts)
        try:
            doc = OKFDocument.parse(md_path.read_text(encoding="utf-8"))
        except OKFDocumentError:
            continue
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
        body = doc.body or ""
        concept = OkfConcept(
            id=concept_id,
            type=str(fm.get("type") or "Unknown"),
            title=str(fm.get("title") or concept_id),
            description=str(fm.get("description") or ""),
            resource=str(fm.get("resource") or ""),
            tags=[str(t) for t in tags],
            body=body,
            links_to=extract_links(body, md_path.parent, bundle_root),
            status=lifecycle_status(fm),
            generated_by=gen_by,
            generated_at=gen_at,
            trust_tier=trust_tier(fm),
            stale_after=stale,
            sources=sources,
            source_document=str(fm.get("source_document") or ""),
            source_lines=str(fm.get("source_lines") or ""),
            section=str(fm.get("section") or ""),
            normative=_normative_value(fm.get("normative")),
            concept_range=str(fm.get("concept_range") or ""),
            frontmatter=dict(fm),
            atomics=parse_atomic_concepts(body, parent_id=concept_id),
        )
        pending.append((concept, md_path.parent))
        concepts.append(concept)

    concept_ids = {c.id for c in concepts}
    for concept, doc_dir in pending:
        concept.source_links_to = source_concept_ids(
            concept.sources, doc_dir, bundle_root, concept_ids
        )
    return concepts


# Backward-compatible private aliases used by older call sites during migration
_RESERVED_NAMES = RESERVED_NAMES
_resolve_md_target = resolve_md_target
_extract_links = extract_links
_walk_concepts = walk_bundle
