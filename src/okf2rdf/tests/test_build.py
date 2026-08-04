from __future__ import annotations

from pathlib import Path

from okf2rdf.build import graph_from_bundle
from okf2rdf.mapping import OKF_NS, SCHEMA, atomic_iri, concept_iri, schema_type_iri
from rdflib import Literal, URIRef
from rdflib.namespace import DCTERMS, PROV, RDF, RDFS, XSD

FIXTURE = Path(__file__).parent / "fixtures" / "mini_bundle"
BASE = "https://example.org/bundle/"


def test_mini_bundle_graph():
    g, concepts = graph_from_bundle(
        FIXTURE, base=BASE, bundle_name="Mini"
    )
    assert len(concepts) == 2
    a = URIRef(concept_iri(BASE, "concepts/a"))
    b = URIRef(concept_iri(BASE, "examples/b"))
    assert (a, RDF.type, URIRef(f"{SCHEMA}CreativeWork")) in g
    assert (a, RDF.type, URIRef(f"{OKF_NS}Concept")) in g
    assert (a, RDFS.label, Literal("Concept A")) in g
    assert (a, URIRef(f"{SCHEMA}name"), Literal("Concept A")) in g
    assert (a, PROV.wasDerivedFrom, URIRef("https://example.com/source")) in g
    assert (a, DCTERMS.references, b) in g
    assert (b, DCTERMS.references, a) in g
    assert (b, RDF.type, URIRef(schema_type_iri("NIAID Blueprint Requirements"))) in g
    assert (b, URIRef(f"{OKF_NS}normative"), Literal(True)) in g
    bundle = URIRef(BASE)
    assert (bundle, URIRef(f"{SCHEMA}hasPart"), a) in g
    assert (bundle, URIRef(f"{OKF_NS}okfVersion"), Literal("0.2")) in g


def test_mini_bundle_atomics():
    g, concepts = graph_from_bundle(FIXTURE, base=BASE, include_atomics=True)
    a = URIRef(concept_iri(BASE, "concepts/a"))
    a1 = URIRef(atomic_iri(BASE, 1))
    a2 = URIRef(atomic_iri(BASE, 2))
    assert (a1, RDF.type, URIRef(f"{OKF_NS}AtomicConcept")) in g
    assert (a1, URIRef(f"{SCHEMA}text"), Literal("Alpha claim one.")) in g
    assert (a1, URIRef(f"{OKF_NS}atomicNumber"), Literal(1, datatype=XSD.integer)) in g
    assert (a1, URIRef(f"{OKF_NS}sourceLines"), Literal("10")) in g
    assert (a1, DCTERMS.isPartOf, a) in g
    assert (a, URIRef(f"{SCHEMA}hasPart"), a1) in g
    assert (a, URIRef(f"{SCHEMA}hasPart"), a2) in g
    assert (a2, URIRef(f"{OKF_NS}sourceLines"), Literal("11-12")) in g
    parent = next(c for c in concepts if c.id == "concepts/a")
    assert len(parent.atomics) == 2


def test_no_atomics_flag():
    g, _ = graph_from_bundle(FIXTURE, base=BASE, include_atomics=False)
    a1 = URIRef(atomic_iri(BASE, 1))
    assert (a1, RDF.type, URIRef(f"{OKF_NS}AtomicConcept")) not in g


def test_no_body_links():
    g, _ = graph_from_bundle(
        FIXTURE, base=BASE, include_body_links=False
    )
    a = URIRef(concept_iri(BASE, "concepts/a"))
    b = URIRef(concept_iri(BASE, "examples/b"))
    assert (a, DCTERMS.references, b) not in g


def test_niaid_smoke():
    repo_bundle = (
        Path(__file__).resolve().parents[3]
        / "okf"
        / "bundles"
        / "niaid_blueprint"
    )
    if not repo_bundle.is_dir():
        import pytest

        pytest.skip("niaid_blueprint not present")
    base = (
        "https://go-fair-us.github.io/ai-blueprint-core/okf/bundles/niaid_blueprint/"
    )
    g, concepts = graph_from_bundle(
        repo_bundle, base=base, bundle_name="NIAID Blueprint", include_atomics=True
    )
    assert len(concepts) == 27
    atomic_type = URIRef(f"{OKF_NS}AtomicConcept")
    atomics = list(g.subjects(RDF.type, atomic_type))
    assert len(atomics) == 239
    # Sample claim under motivation
    a118 = URIRef(atomic_iri(base, 118))
    parent = URIRef(concept_iri(base, "api-specification/motivation"))
    assert (a118, DCTERMS.isPartOf, parent) in g
    texts = list(g.objects(a118, URIRef(f"{SCHEMA}text")))
    assert texts and "repository landscape" in str(texts[0])
