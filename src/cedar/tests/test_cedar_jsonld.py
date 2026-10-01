from __future__ import annotations

import json
from datetime import datetime, timezone

from defs.cedar_jsonld import cedar_to_record, load_template, record_to_cedar
from defs.models import (
    DatasetRecord,
    LicenseRecord,
    TemporalCoverage,
    Term,
)
from defs.paths import EXAMPLE_PATH, TOOL_IRI

NOW = datetime(2026, 8, 23, 12, 0, tzinfo=timezone.utc)


def _actt4() -> DatasetRecord:
    return DatasetRecord(
        type=Term(iri="http://purl.org/dc/dcmitype/Dataset", label="Dataset"),
        name="(Released May 2022) Adaptive COVID-19 Treatment Trial 4 (ACTT-4)",
        description=(
            "The dataset includes patient-level data from the ACTT-4 study, covering "
            "demographics (age, gender, comorbidities), treatment arms "
            "(baricitinib + remdesivir or dexamethasone + remdesivir… "
        ),
        date_created="2022-05-01",
        author_persons=[
            Term(iri="https://orcid.org/0000-0001-8922-0488", label="Nina Kreuzberger"),
            Term(iri="https://orcid.org/0000-0002-2011-1010", label="Caroline Hirsch"),
        ],
        funder=[
            Term(
                iri="https://ror.org/043z4tv69",
                label="National Institute of Allergy and Infectious Diseases",
            )
        ],
        grant=[
            "UM1AI148684",
            "UM1AI148576",
            "UM1AI148575",
            "UM1AI148685",
            "UM1AI148450",
            "UM1AI148689",
        ],
        measurement_technique=[
            Term(
                iri="http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C83312",
                label="Laboratory Test Method",
            )
        ],
        distribution=[
            "https://accessclinicaldata.niaid.nih.gov/study-viewer/clinical_trials/NCT04640168"
        ],
        citation=[
            "https://www.thelancet.com/journals/lanres/article/PIIS2213-2600(22)00088-1/fulltext"
        ],
        infectious_agent=[
            Term(
                iri="http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C169076",
                label="SARS Coronavirus 2",
            )
        ],
        host=[
            Term(
                iri="http://purl.bioontology.org/ontology/NCBITAXON/9606",
                label="Homo sapiens",
            )
        ],
        health_condition=[
            Term(
                iri="http://purl.obolibrary.org/obo/MONDO_0100096",
                label="COVID-19",
            )
        ],
        conditions_of_access=[
            "https://accessclinicaldata.niaid.nih.gov/dashboard/Public/files/NIAID_DAR.pdf"
        ],
        license=LicenseRecord(
            iri="https://accessclinicaldata.niaid.nih.gov/dashboard/Public/files/NIAIDDUA2021Accessclinicaldata@NIAID.pdf"
        ),
        temporal_coverage=[
            TemporalCoverage(start="2020-11-24T00:00:00", end="2021-06-30T00:00:00")
        ],
    )


def test_output_has_template_keys():
    template = json.loads(EXAMPLE_PATH.read_text())
    doc = record_to_cedar(_actt4(), now=NOW, instance_id="urn:uuid:test")
    assert set(doc) == set(template)


def test_context_and_template_iri_copied():
    template = load_template()
    doc = record_to_cedar(_actt4(), now=NOW, instance_id="urn:uuid:test")
    assert doc["@context"] == template["@context"]
    assert doc["schema:isBasedOn"] == template["schema:isBasedOn"]
    assert doc["schema:name"] == template["schema:name"]
    assert doc["pav:createdBy"] == TOOL_IRI
    assert doc["@id"] == "urn:uuid:test"


def test_actt4_payload_shapes():
    gold = json.loads(EXAMPLE_PATH.read_text())
    doc = record_to_cedar(_actt4(), now=NOW, instance_id="urn:uuid:test")
    assert doc["type"] == gold["type"]
    assert doc["name"] == gold["name"]
    assert doc["dateCreated"] == gold["dateCreated"]
    assert doc["funder"] == gold["funder"]
    assert doc["grant"] == gold["grant"]
    assert doc["Author"]["author-person"] == gold["Author"]["author-person"]
    assert doc["Author"]["author-organization"] == [{}]
    assert doc["distribution"] == gold["distribution"]
    assert doc["citation"] == gold["citation"]
    assert doc["infectiousAgent"] == gold["infectiousAgent"]
    assert doc["host"] == gold["host"]
    assert doc["healthCondition"] == gold["healthCondition"]
    assert doc["LIcense(s)"]["licenseIRI"] == gold["LIcense(s)"]["licenseIRI"]
    assert doc["Temporal Coverage"][0]["startTime"] == gold["Temporal Coverage"][0]["startTime"]
    assert doc["Temporal Coverage"][0]["endTime"] == gold["Temporal Coverage"][0]["endTime"]
    assert "@context" in doc["Author"]
    assert "@context" in doc["LIcense(s)"]
    assert "@context" in doc["Spatial Coverage"]
    assert "@context" in doc["Temporal Coverage"][0]


def test_empty_record_keeps_template_shape():
    template = json.loads(EXAMPLE_PATH.read_text())
    doc = record_to_cedar(DatasetRecord(), now=NOW, instance_id="urn:uuid:empty")
    assert set(doc) == set(template)
    assert doc["identifier"] == {}
    assert doc["type"] == {}
    assert doc["name"] == {"@value": None}
    assert doc["Author"]["author-person"] == [{}]
    assert doc["Author"]["author-organization"] == [{}]
    assert doc["LIcense(s)"]["licenseIdentifier"] == [{}]
    assert doc["LIcense(s)"]["licenseDescription"] == [{"@value": None}]
    assert doc["Spatial Coverage"]["countryCode"] == [{}]
    assert doc["Spatial Coverage"]["geoCoordinates"] == [{"@value": None}]
    assert len(doc["Temporal Coverage"]) == 1
    assert doc["Temporal Coverage"][0]["startTime"]["@value"] is None


def test_cedar_to_record_example_payload():
    gold = json.loads(EXAMPLE_PATH.read_text())
    rec = cedar_to_record(gold)
    assert rec.name and rec.name.startswith("(Released May 2022)")
    assert rec.grant[0] == "UM1AI148684"
    assert rec.author_persons[0].iri and rec.author_persons[0].iri.endswith("8922-0488")
    assert rec.citation[0].startswith("https://www.thelancet.com")
    assert rec.funder[0].iri == "https://ror.org/043z4tv69"
    assert rec.license and rec.license.iri and "NIAIDDUA" in rec.license.iri


def test_month_only_temporal_is_valid_datetime():
    rec = DatasetRecord(
        temporal_coverage=[TemporalCoverage(start="2020-11", end="2021-06T00:00:00")]
    )
    doc = record_to_cedar(rec, now=NOW, instance_id="urn:uuid:t")
    start = doc["Temporal Coverage"][0]["startTime"]["@value"]
    end = doc["Temporal Coverage"][0]["endTime"]["@value"]
    assert start == "2020-11-01T00:00:00"
    assert end == "2021-06-01T00:00:00"
    assert "2020-11T" not in start


def test_quoted_name_serialized_clean():
    rec = DatasetRecord(name='"ACTT-4"')
    doc = record_to_cedar(rec, now=NOW, instance_id="urn:uuid:q")
    assert doc["name"]["@value"] == "ACTT-4"
