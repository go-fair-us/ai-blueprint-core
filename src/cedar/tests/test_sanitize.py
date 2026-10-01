from defs.models import DatasetRecord, Term
from defs.program import sanitize_record


def test_patient_level_data_becomes_dataset():
    rec = DatasetRecord(
        name="Adaptive COVID-19 Treatment Trial 4 (ACTT-4)",
        type=Term(label="Patient-Level Data"),
        identifier='"NCT04640168"',
    )
    out = sanitize_record(rec)
    assert out.type is not None
    assert out.type.iri == "http://purl.org/dc/dcmitype/Dataset"
    assert out.identifier == "NCT04640168"
