"""Build an rdflib Graph from walked OKF concepts (and optional atomics)."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

from okf_core.atomic import AtomicConcept
from okf_core.document import OKFDocument, OKFDocumentError
from okf_core.walk import OkfConcept, walk_bundle
from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, PROV, RDF, RDFS, XSD
from rdflib.namespace import SKOS

from okf2rdf.mapping import (
    OKF_NS,
    SCHEMA,
    agent_iri,
    atomic_iri,
    bundle_iri,
    concept_iri,
    schema_type_iri,
    short_label,
)

SDO = Namespace(SCHEMA)
OKF = Namespace(OKF_NS)


def _is_absolute_http(url: str) -> bool:
    try:
        p = urlparse(url)
        return p.scheme in ("http", "https") and bool(p.netloc)
    except Exception:
        return False


def _read_okf_version(bundle_root: Path) -> str | None:
    index = Path(bundle_root) / "index.md"
    if not index.is_file():
        return None
    try:
        doc = OKFDocument.parse(index.read_text(encoding="utf-8"))
    except OKFDocumentError:
        return None
    ver = (doc.frontmatter or {}).get("okf_version")
    return str(ver) if ver is not None else None


def _emit_atomic(
    g: Graph,
    atomic: AtomicConcept,
    parent: OkfConcept,
    parent_uri: URIRef,
    *,
    base: str,
    ensure_agent,
) -> URIRef:
    """Emit one atomic concept node; return its URIRef."""
    a_uri = URIRef(atomic_iri(base, atomic.number))
    g.add((a_uri, RDF.type, OKF.AtomicConcept))
    g.add((a_uri, RDF.type, SDO.CreativeWork))
    g.add((a_uri, OKF.atomicNumber, Literal(atomic.number, datatype=XSD.integer)))
    g.add((a_uri, SKOS.notation, Literal(str(atomic.number))))
    g.add((a_uri, OKF.conceptId, Literal(atomic.concept_id)))
    g.add((a_uri, SDO.text, Literal(atomic.text)))
    g.add((a_uri, RDFS.comment, Literal(atomic.text)))
    g.add((a_uri, RDFS.label, Literal(short_label(atomic.text))))
    if atomic.source_lines:
        g.add((a_uri, OKF.sourceLines, Literal(atomic.source_lines)))
    g.add((a_uri, DCTERMS.isPartOf, parent_uri))
    g.add((parent_uri, SDO.hasPart, a_uri))

    if parent.normative is not None:
        g.add((a_uri, OKF.normative, Literal(parent.normative, datatype=XSD.boolean)))
    if parent.status:
        g.add((a_uri, SDO.creativeWorkStatus, Literal(parent.status)))
    if parent.resource and _is_absolute_http(parent.resource):
        g.add((a_uri, PROV.wasDerivedFrom, URIRef(parent.resource)))
    # Light PROV inheritance from parent generation
    if parent.generated_at:
        g.add(
            (
                a_uri,
                PROV.generatedAtTime,
                Literal(parent.generated_at, datatype=XSD.dateTime),
            )
        )
    if parent.generated_by:
        g.add((a_uri, PROV.wasAttributedTo, ensure_agent(parent.generated_by)))
    return a_uri


def build_graph(
    concepts: list[OkfConcept],
    *,
    base: str,
    bundle_name: str,
    okf_version: str | None = None,
    include_body_links: bool = True,
    include_atomics: bool = True,
) -> Graph:
    """Construct RDF graph for a list of OKF concepts."""
    g = Graph()
    g.bind("schema", SDO)
    g.bind("prov", PROV)
    g.bind("dcterms", DCTERMS)
    g.bind("rdfs", RDFS)
    g.bind("rdf", RDF)
    g.bind("xsd", XSD)
    g.bind("skos", SKOS)
    g.bind("okf", OKF)

    ids = {c.id for c in concepts}
    b_iri = URIRef(bundle_iri(base))
    g.add((b_iri, RDF.type, SDO.Collection))
    g.add((b_iri, RDF.type, OKF.Bundle))
    g.add((b_iri, SDO.name, Literal(bundle_name)))
    g.add((b_iri, RDFS.label, Literal(bundle_name)))
    if okf_version:
        g.add((b_iri, OKF.okfVersion, Literal(okf_version)))

    agents_seen: set[str] = set()

    def ensure_agent(actor: str) -> URIRef:
        airi = agent_iri(base, actor)
        if airi not in agents_seen:
            agents_seen.add(airi)
            node = URIRef(airi)
            if actor.startswith("human:"):
                g.add((node, RDF.type, PROV.Person))
                g.add((node, RDF.type, SDO.Person))
            elif actor.startswith("process:"):
                g.add((node, RDF.type, PROV.SoftwareAgent))
            else:
                g.add((node, RDF.type, PROV.SoftwareAgent))
            g.add((node, RDFS.label, Literal(actor)))
        return URIRef(airi)

    for c in concepts:
        subj = URIRef(concept_iri(base, c.id))
        g.add((subj, RDF.type, URIRef(schema_type_iri(c.type))))
        g.add((subj, RDF.type, OKF.Concept))
        g.add((subj, OKF.okfType, Literal(c.type)))
        g.add((subj, OKF.conceptId, Literal(c.id)))

        if c.title:
            g.add((subj, SDO.name, Literal(c.title)))
            g.add((subj, RDFS.label, Literal(c.title)))
        if c.description:
            g.add((subj, SDO.description, Literal(c.description)))
        if c.resource:
            if _is_absolute_http(c.resource):
                g.add((subj, SDO.url, URIRef(c.resource)))
            else:
                g.add((subj, RDFS.seeAlso, Literal(c.resource)))
        for tag in c.tags:
            g.add((subj, SDO.keywords, Literal(tag)))
        if c.status:
            g.add((subj, SDO.creativeWorkStatus, Literal(c.status)))
        if c.stale_after:
            g.add((subj, SDO.expires, Literal(c.stale_after, datatype=XSD.date)))
        if c.generated_at:
            g.add(
                (
                    subj,
                    PROV.generatedAtTime,
                    Literal(c.generated_at, datatype=XSD.dateTime),
                )
            )
        if c.generated_by:
            g.add((subj, PROV.wasAttributedTo, ensure_agent(c.generated_by)))
        if c.trust_tier:
            g.add((subj, OKF.trustTier, Literal(c.trust_tier)))
        if c.source_document:
            g.add((subj, DCTERMS.source, Literal(c.source_document)))
        if c.source_lines:
            g.add((subj, OKF.sourceLines, Literal(c.source_lines)))
        if c.section:
            g.add((subj, SDO.headline, Literal(c.section)))
        if c.normative is not None:
            g.add((subj, OKF.normative, Literal(c.normative, datatype=XSD.boolean)))
        if c.concept_range:
            g.add((subj, OKF.conceptRange, Literal(c.concept_range)))

        for src in c.sources:
            res = src.get("resource") or ""
            if res and _is_absolute_http(res):
                g.add((subj, PROV.wasDerivedFrom, URIRef(res)))
                g.add((subj, DCTERMS.source, URIRef(res)))
            elif res:
                g.add((subj, DCTERMS.source, Literal(res)))
            if src.get("title") or src.get("author") or src.get("id"):
                cit = BNode()
                g.add((subj, SDO.citation, cit))
                g.add((cit, RDF.type, SDO.CreativeWork))
                if src.get("title"):
                    g.add((cit, SDO.name, Literal(src["title"])))
                if src.get("id"):
                    g.add((cit, SDO.identifier, Literal(src["id"])))
                if res and _is_absolute_http(res):
                    g.add((cit, SDO.url, URIRef(res)))
                if src.get("author"):
                    g.add((cit, SDO.author, ensure_agent(src["author"])))

        if include_body_links:
            for target in c.links_to:
                if target in ids:
                    g.add(
                        (
                            subj,
                            DCTERMS.references,
                            URIRef(concept_iri(base, target)),
                        )
                    )
        for target in c.source_links_to:
            if target in ids:
                g.add(
                    (
                        subj,
                        PROV.wasDerivedFrom,
                        URIRef(concept_iri(base, target)),
                    )
                )

        g.add((b_iri, SDO.hasPart, subj))
        g.add((subj, DCTERMS.isPartOf, b_iri))

        if include_atomics:
            for atomic in c.atomics:
                a_uri = _emit_atomic(
                    g, atomic, c, subj, base=base, ensure_agent=ensure_agent
                )
                # Bundle also lists atomics as parts (query convenience)
                g.add((b_iri, SDO.hasPart, a_uri))

    return g


def graph_from_bundle(
    bundle_root: Path,
    *,
    base: str,
    bundle_name: str | None = None,
    include_body_links: bool = True,
    include_atomics: bool = True,
) -> tuple[Graph, list[OkfConcept]]:
    """Walk bundle and build graph. Returns (graph, concepts)."""
    bundle_root = Path(bundle_root)
    concepts = walk_bundle(bundle_root)
    name = bundle_name or bundle_root.resolve().name
    version = _read_okf_version(bundle_root)
    g = build_graph(
        concepts,
        base=base,
        bundle_name=name,
        okf_version=version,
        include_body_links=include_body_links,
        include_atomics=include_atomics,
    )
    return g, concepts
