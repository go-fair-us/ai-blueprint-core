from okf2rdf.mapping import (
    agent_iri,
    atomic_iri,
    concept_iri,
    schema_type_iri,
    short_label,
)


def test_concept_iri():
    assert (
        concept_iri("https://ex.org/b/", "metadata-schema/requirements")
        == "https://ex.org/b/metadata-schema/requirements"
    )
    assert concept_iri("https://ex.org/b", "a/b") == "https://ex.org/b/a/b"


def test_atomic_iri():
    assert atomic_iri("https://ex.org/b/", 118) == "https://ex.org/b/atomic/118"
    assert atomic_iri("https://ex.org/b", 1) == "https://ex.org/b/atomic/1"


def test_short_label():
    assert short_label("short") == "short"
    long = "x" * 100
    assert len(short_label(long)) == 80
    assert short_label(long).endswith("…")


def test_schema_type_iri():
    assert schema_type_iri("NIAID Blueprint Requirements").endswith("TechArticle")
    assert schema_type_iri("Unknown Type").endswith("CreativeWork")


def test_agent_iri():
    iri = agent_iri("https://ex.org/b/", "niaid-bp-okf-migrate/0.2")
    assert iri.startswith("https://ex.org/b/agents/")
    assert "niaid-bp-okf-migrate" in iri
