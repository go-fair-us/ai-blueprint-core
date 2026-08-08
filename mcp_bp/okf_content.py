"""OKF bundle and prompt-example access for the Blueprint MCP server.

Wraps ``okf_core.walk_bundle`` with a process-lifetime cache, JSON-safe
serializers, filters, and safe reads of concept Markdown / prompt examples.
"""

from __future__ import annotations

import sys
from pathlib import Path

from .config import (
    OKF_BUNDLES_DIR,
    OKF_DEFAULT_BUNDLE,
    OKF_ENABLED,
    OKF_PROMPT_EXAMPLES_DIR,
    REPO_ROOT,
)
from .content import list_markdown, read_markdown

# Ensure okf_core is importable without a hard install (monorepo layout).
_OKF_CORE_SRC = REPO_ROOT / "src" / "okf_core" / "src"
if _OKF_CORE_SRC.is_dir() and str(_OKF_CORE_SRC) not in sys.path:
    sys.path.insert(0, str(_OKF_CORE_SRC))

from okf_core import (  # noqa: E402
    AtomicConcept,
    OkfConcept,
    walk_bundle,
)

# Concept id path segments that map to FAIR / Blueprint pillars.
_PILLAR_PREFIXES: dict[str, str] = {
    "metadata": "metadata-schema",
    "identifiers": "persistent-identifiers",
    "api": "api-specification",
    "citation": "citation",
    "outreach": "outreach-training",
}

KNOWN_OKF_PILLARS: list[str] = list(_PILLAR_PREFIXES.keys())

# Process-lifetime cache: bundle name -> list of OkfConcept
_BUNDLE_CACHE: dict[str, list[OkfConcept]] = {}


class OkfError(Exception):
    """Raised when an OKF bundle or concept cannot be resolved."""


def okf_available() -> bool:
    """Return True when OKF serving is enabled and the bundles root exists."""
    return OKF_ENABLED and OKF_BUNDLES_DIR.is_dir()


def invalidate_cache() -> None:
    """Drop cached walk_bundle results (e.g. after test monkeypatches)."""
    _BUNDLE_CACHE.clear()


def list_bundles() -> list[dict[str, object]]:
    """List available OKF bundle directories under ``OKF_BUNDLES_DIR``."""
    if not okf_available():
        return []
    out: list[dict[str, object]] = []
    for path in sorted(OKF_BUNDLES_DIR.iterdir()):
        if not path.is_dir():
            continue
        index = path / "index.md"
        out.append(
            {
                "name": path.name,
                "path": path.as_posix(),
                "has_index": index.is_file(),
                "is_default": path.name == OKF_DEFAULT_BUNDLE,
            }
        )
    return out


def _resolve_bundle(bundle: str | None) -> Path:
    if not okf_available():
        raise OkfError(
            "OKF content is disabled or the bundles directory is missing. "
            f"Expected {OKF_BUNDLES_DIR}."
        )
    name = (bundle or OKF_DEFAULT_BUNDLE).strip()
    if not name or "/" in name or "\\" in name or name in (".", ".."):
        raise OkfError(f"Invalid bundle name: {name!r}")
    root = (OKF_BUNDLES_DIR / name).resolve()
    base = OKF_BUNDLES_DIR.resolve()
    if base != root and base not in root.parents:
        raise OkfError(f"Bundle path escapes OKF_BUNDLES_DIR: {name!r}")
    if not root.is_dir():
        raise OkfError(f"Unknown OKF bundle: {name!r}")
    return root


def get_concepts(bundle: str | None = None) -> list[OkfConcept]:
    """Return cached ``walk_bundle`` results for ``bundle`` (or the default)."""
    name = (bundle or OKF_DEFAULT_BUNDLE).strip()
    if name in _BUNDLE_CACHE:
        return _BUNDLE_CACHE[name]
    root = _resolve_bundle(name)
    concepts = walk_bundle(root)
    _BUNDLE_CACHE[name] = concepts
    return concepts


def _atomic_as_dict(a: AtomicConcept) -> dict[str, object]:
    return {
        "number": a.number,
        "text": a.text,
        "source_lines": a.source_lines,
        "parent_id": a.parent_id,
        "concept_id": a.concept_id,
    }


def concept_summary(c: OkfConcept) -> dict[str, object]:
    """Lightweight catalog entry (no body)."""
    return {
        "id": c.id,
        "type": c.type,
        "title": c.title,
        "description": c.description,
        "tags": list(c.tags),
        "status": c.status,
        "normative": c.normative,
        "section": c.section,
        "source_lines": c.source_lines,
        "concept_range": c.concept_range,
        "atomic_count": len(c.atomics),
        "links_to": list(c.links_to),
    }


def concept_as_dict(c: OkfConcept, *, include_body: bool = True) -> dict[str, object]:
    """Full structured concept payload for tools."""
    data = concept_summary(c)
    data.update(
        {
            "resource": c.resource,
            "sources": list(c.sources),
            "generated_by": c.generated_by,
            "generated_at": c.generated_at,
            "trust_tier": c.trust_tier,
            "stale_after": c.stale_after,
            "source_document": c.source_document,
            "source_links_to": list(c.source_links_to),
            "atomics": [_atomic_as_dict(a) for a in c.atomics],
        }
    )
    if include_body:
        data["body"] = c.body
    return data


def list_concepts(
    bundle: str | None = None,
    *,
    type: str | None = None,
    prefix: str | None = None,
    tag: str | None = None,
    normative: bool | None = None,
) -> list[dict[str, object]]:
    """Filter and list concept summaries."""
    concepts = get_concepts(bundle)
    out: list[dict[str, object]] = []
    type_l = type.lower().strip() if type else None
    prefix_s = prefix.strip().rstrip("/") if prefix else None
    tag_l = tag.lower().strip() if tag else None

    for c in concepts:
        if type_l and type_l not in c.type.lower():
            continue
        if prefix_s and not (
            c.id == prefix_s or c.id.startswith(prefix_s + "/")
        ):
            continue
        if tag_l and not any(tag_l == t.lower() for t in c.tags):
            continue
        if normative is not None and c.normative is not normative:
            continue
        out.append(concept_summary(c))
    return out


def get_concept(concept_id: str, bundle: str | None = None) -> OkfConcept:
    """Look up one concept by path id (e.g. ``metadata-schema/requirements``)."""
    cid = concept_id.strip().lstrip("/")
    if cid.endswith(".md"):
        cid = cid[:-3]
    for c in get_concepts(bundle):
        if c.id == cid:
            return c
    raise OkfError(
        f"Concept not found: {concept_id!r}. "
        "Use list_okf_concepts() for available ids."
    )


def read_concept_markdown(concept_id: str, bundle: str | None = None) -> str:
    """Return the raw Markdown file for a concept (frontmatter + body)."""
    root = _resolve_bundle(bundle)
    cid = concept_id.strip().lstrip("/")
    if cid.endswith(".md"):
        rel = cid
    else:
        rel = cid + ".md"
    return read_markdown(root, rel)


def read_bundle_index(bundle: str | None = None) -> str:
    """Return root ``index.md`` for progressive disclosure."""
    root = _resolve_bundle(bundle)
    index = root / "index.md"
    if not index.is_file():
        raise OkfError(f"No index.md in bundle {(bundle or OKF_DEFAULT_BUNDLE)!r}")
    return index.read_text(encoding="utf-8", errors="replace")


def get_atomic(
    number: int, bundle: str | None = None
) -> dict[str, object]:
    """Return one atomic concept by global number."""
    for c in get_concepts(bundle):
        for a in c.atomics:
            if a.number == number:
                data = _atomic_as_dict(a)
                data["parent_title"] = c.title
                data["parent_type"] = c.type
                data["parent_section"] = c.section
                return data
    raise OkfError(f"Atomic concept #{number} not found in bundle.")


def list_atomics(
    bundle: str | None = None,
    *,
    parent_id: str | None = None,
    query: str | None = None,
    max_results: int = 50,
) -> list[dict[str, object]]:
    """List atomic claims, optionally filtered by parent concept or substring."""
    parent = parent_id.strip().lstrip("/") if parent_id else None
    if parent and parent.endswith(".md"):
        parent = parent[:-3]
    q = query.lower().strip() if query else None
    out: list[dict[str, object]] = []
    for c in get_concepts(bundle):
        if parent and c.id != parent:
            continue
        for a in c.atomics:
            if q and q not in a.text.lower():
                continue
            data = _atomic_as_dict(a)
            data["parent_title"] = c.title
            out.append(data)
            if len(out) >= max_results:
                return out
    return out


def get_related(concept_id: str, bundle: str | None = None) -> dict[str, object]:
    """Return outbound links and reverse links for a concept."""
    concepts = get_concepts(bundle)
    by_id = {c.id: c for c in concepts}
    c = by_id.get(concept_id.strip().lstrip("/").removesuffix(".md"))
    if c is None:
        raise OkfError(f"Concept not found: {concept_id!r}")
    outbound = [
        concept_summary(by_id[t]) for t in c.links_to if t in by_id
    ]
    inbound = [
        concept_summary(other)
        for other in concepts
        if c.id in other.links_to
    ]
    return {
        "id": c.id,
        "links_to": outbound,
        "linked_from": inbound,
    }


def get_requirements(
    pillar: str | None = None, bundle: str | None = None
) -> dict[str, object]:
    """Return OKF requirements concepts for a FAIR pillar (or an index of all).

    Pillar keys match the Blueprint MCP tools: ``metadata``, ``identifiers``,
    ``api``, ``citation``, ``outreach``.
    """
    concepts = get_concepts(bundle)

    def _is_requirements(c: OkfConcept) -> bool:
        return (
            c.id.endswith("/requirements")
            or "requirements" in c.type.lower()
        )

    if pillar is None:
        summary: dict[str, list[dict[str, object]]] = {}
        for key, prefix in _PILLAR_PREFIXES.items():
            summary[key] = [
                concept_summary(c)
                for c in concepts
                if c.id.startswith(prefix) and _is_requirements(c)
            ]
        return {
            "pillars": summary,
            "available_pillars": KNOWN_OKF_PILLARS,
            "note": (
                "OKF requirements are structured concept graphs with atomic "
                "claims. For full narrative Blueprint text use "
                "get_blueprint_requirements / get_blueprint_section."
            ),
        }

    p = pillar.lower().strip()
    matched_key: str | None = None
    for key, prefix in _PILLAR_PREFIXES.items():
        if p == key or p in prefix or p in key:
            matched_key = key
            break
    # Also accept directory names directly.
    if matched_key is None:
        for key, prefix in _PILLAR_PREFIXES.items():
            if p == prefix:
                matched_key = key
                break
    if matched_key is None:
        raise OkfError(
            f"Unknown OKF pillar {pillar!r}. "
            f"Valid options: {KNOWN_OKF_PILLARS}"
        )

    prefix = _PILLAR_PREFIXES[matched_key]
    matched = [
        concept_as_dict(c)
        for c in concepts
        if c.id.startswith(prefix) and _is_requirements(c)
    ]
    if not matched:
        # Fall back to any requirements-like under prefix.
        matched = [
            concept_as_dict(c)
            for c in concepts
            if c.id == f"{prefix}/requirements"
            or (c.id.startswith(prefix + "/") and "requirement" in c.id)
        ]
    return {"pillar": matched_key, "prefix": prefix, "concepts": matched}


def okf_stats(bundle: str | None = None) -> dict[str, object]:
    """Corpus statistics for the OKF default (or named) bundle."""
    if not okf_available():
        return {
            "enabled": False,
            "bundles_dir": str(OKF_BUNDLES_DIR),
            "bundles": [],
        }
    name = bundle or OKF_DEFAULT_BUNDLE
    concepts = get_concepts(name)
    types: dict[str, int] = {}
    for c in concepts:
        types[c.type] = types.get(c.type, 0) + 1
    atomic_total = sum(len(c.atomics) for c in concepts)
    examples = list_prompt_examples()
    return {
        "enabled": True,
        "bundles_dir": str(OKF_BUNDLES_DIR),
        "default_bundle": OKF_DEFAULT_BUNDLE,
        "bundle": name,
        "bundles": list_bundles(),
        "concepts": len(concepts),
        "atomics": atomic_total,
        "types": types,
        "prompt_examples": len(examples),
    }


# --- Prompt examples -------------------------------------------------------


def list_prompt_examples() -> list[dict[str, object]]:
    """List Markdown files under ``OKF_PROMPT_EXAMPLES_DIR``."""
    if not OKF_PROMPT_EXAMPLES_DIR.is_dir():
        return []
    return [e.as_dict() for e in list_markdown(OKF_PROMPT_EXAMPLES_DIR)]


def read_prompt_example(relative_path: str) -> str:
    """Read a single prompt-example Markdown file."""
    if not OKF_PROMPT_EXAMPLES_DIR.is_dir():
        raise OkfError(
            f"Prompt examples directory not found: {OKF_PROMPT_EXAMPLES_DIR}"
        )
    return read_markdown(OKF_PROMPT_EXAMPLES_DIR, relative_path)


def search_chunks_for_index(
    bundle: str | None = None,
) -> list[dict[str, str | None]]:
    """Emit concept- and atomic-level chunks for hybrid search indexing.

    Each dict has keys: ``chunk_id``, ``source``, ``path``, ``section_number``,
    ``section_title``, ``body``.
    """
    if not okf_available():
        return []
    try:
        concepts = get_concepts(bundle)
    except OkfError:
        return []

    chunks: list[dict[str, str | None]] = []
    for c in concepts:
        # Concept-level chunk (prose without the atomic table is ideal, but
        # full body is acceptable and simpler).
        prose = c.body
        # Prefer body above the atomic table for concept chunks.
        marker = "# Atomic concepts"
        if marker in prose:
            prose = prose.split(marker, 1)[0].strip()
        concept_body = f"{c.title}\n{c.description}\n{prose}".strip()
        if concept_body:
            chunks.append(
                {
                    "chunk_id": f"okf::{c.id}::concept",
                    "source": "okf",
                    "path": c.id,
                    "section_number": c.concept_range or None,
                    "section_title": c.title,
                    "body": concept_body,
                }
            )
        for a in c.atomics:
            chunks.append(
                {
                    "chunk_id": f"okf::atomic/{a.number}",
                    "source": "okf",
                    "path": f"atomic/{a.number}",
                    "section_number": str(a.number),
                    "section_title": f"Atomic {a.number} ({c.id})",
                    "body": a.text,
                }
            )
    return chunks
