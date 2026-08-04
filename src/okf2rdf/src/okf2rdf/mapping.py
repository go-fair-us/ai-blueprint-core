"""OKF field and type maps → schema.org / PROV / DCTERMS / RDFS / local okf:."""

from __future__ import annotations

from urllib.parse import quote

# Fixed local vocabulary for OKF-specific predicates (portable across --base).
OKF_NS = "https://go-fair-us.github.io/ai-blueprint-core/ns/okf#"

SCHEMA = "https://schema.org/"
PROV = "http://www.w3.org/ns/prov#"
DCTERMS = "http://purl.org/dc/terms/"
RDFS = "http://www.w3.org/2000/01/rdf-schema#"
RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
XSD = "http://www.w3.org/2001/XMLSchema#"
SKOS = "http://www.w3.org/2004/02/skos/core#"

# OKF free-text type → primary schema.org class local name
TYPE_TO_SCHEMA: dict[str, str] = {
    "NIAID Blueprint Section": "Article",
    "NIAID Blueprint Requirements": "TechArticle",
    "Reference Table": "Table",
    "Worked Example": "CreativeWork",
    "Document Status": "DigitalDocument",
    "Concept": "CreativeWork",
    "Reference": "CreativeWork",
    "Skill Bundle Example": "CreativeWork",
    "Publication": "ScholarlyArticle",
    "Paper": "ScholarlyArticle",
    "BigQuery Dataset": "Dataset",
    "BigQuery Table": "Dataset",
    "Attested Computation": "SoftwareSourceCode",
    "Metrics": "CreativeWork",
}
DEFAULT_SCHEMA_TYPE = "CreativeWork"


def schema_type_iri(okf_type: str) -> str:
    local = TYPE_TO_SCHEMA.get(okf_type, DEFAULT_SCHEMA_TYPE)
    return f"{SCHEMA}{local}"


def concept_iri(base: str, concept_id: str) -> str:
    """Mint subject IRI from --base and OKF path concept id."""
    base_n = base.rstrip("/") + "/"
    # Encode each path segment; keep slashes as hierarchy
    parts = [quote(p, safe="") for p in concept_id.split("/") if p]
    return base_n + "/".join(parts)


def atomic_iri(base: str, number: int, *, prefix: str = "atomic") -> str:
    """Mint subject IRI for a global atomic concept number: ``{base}atomic/{n}``."""
    base_n = base.rstrip("/") + "/"
    seg = quote(prefix.strip("/"), safe="")
    return f"{base_n}{seg}/{int(number)}"


def short_label(text: str, max_len: int = 80) -> str:
    """Truncate claim text for rdfs:label."""
    text = (text or "").strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"


def agent_iri(base: str, actor: str) -> str:
    """Mint a PROV agent IRI under {base}agents/ from actor string."""
    base_n = base.rstrip("/") + "/"
    slug = quote(actor.replace("/", "_").replace(":", "_").replace(" ", "_"), safe="_-.")
    return f"{base_n}agents/{slug}"


def bundle_iri(base: str) -> str:
    return base.rstrip("/") + "/"
