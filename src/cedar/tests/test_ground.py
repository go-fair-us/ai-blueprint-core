from defs.ground import ground_record
from defs.models import DatasetRecord, Term


def test_invented_orcid_is_stripped():
    rec = DatasetRecord(
        author_persons=[
            Term(iri="https://orcid.org/0000-0001-2345-6789", label="Ada Lovelace")
        ]
    )
    blob = "Ada Lovelace led the study. No ORCID is listed."
    out, dropped = ground_record(rec, blob)
    assert out.author_persons == [Term(label="Ada Lovelace")]
    assert any(item.field == "author_persons.iri" for item in dropped)


def test_verbatim_grant_kept():
    rec = DatasetRecord(grant=["UM1AI148684", "FAKEGRANT"])
    blob = "Funding: UM1AI148684 from NIAID."
    out, dropped = ground_record(rec, blob)
    assert out.grant == ["UM1AI148684"]
    assert [d.value for d in dropped] == ["FAKEGRANT"]


def test_doi_expansion():
    rec = DatasetRecord(identifier="https://doi.org/10.1234/abc")
    blob = "The paper is 10.1234/abc in the header."
    out, dropped = ground_record(rec, blob)
    assert out.identifier == "https://doi.org/10.1234/abc"
    assert dropped == []


def test_quoted_identifier_survives_grounding():
    rec = DatasetRecord(identifier='"NCT04640168"')
    blob = "NCT Number\nNCT04640168\nSponsor NIAID"
    out, dropped = ground_record(rec, blob)
    assert out.identifier == "NCT04640168"
    assert dropped == []


def test_none_iri_is_not_logged():
    rec = DatasetRecord(funder=[Term(iri="None", label="NIAID")])
    blob = "Sponsor National Institute of Allergy and Infectious Diseases (NIAID)"
    out, dropped = ground_record(rec, blob)
    assert out.funder[0].iri is None
    assert out.funder[0].label == "NIAID"
    assert not any(item.value in {"None", None} for item in dropped)


def test_relative_pdf_url_kept():
    rec = DatasetRecord(
        distribution=[
            "https://accessclinicaldata.niaid.nih.gov/api/files/NCT04640168/ACTT-4_Data_Use_Limitations.pdf"
        ]
    )
    blob = "Study Documents [ACTT-4_Data_Use_Limitations.pdf](/api/files/NCT04640168/ACTT-4_Data_Use_Limitations.pdf)"
    out, dropped = ground_record(rec, blob)
    assert rec.distribution[0] in out.distribution or out.distribution
    assert dropped == []


def test_dcmi_dataset_type_kept_without_iri_on_page():
    rec = DatasetRecord(
        type=Term(iri="http://purl.org/dc/dcmitype/Dataset", label="Dataset"),
        name="A study",
    )
    out, dropped = ground_record(rec, "A study of influenza.")
    assert out.type is not None
    assert out.type.iri == "http://purl.org/dc/dcmitype/Dataset"
    assert not any(d.field.startswith("type") for d in dropped)
