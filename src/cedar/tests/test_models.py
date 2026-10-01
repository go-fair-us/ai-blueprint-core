from defs.models import DatasetRecord, Term


def test_empty_record_defaults():
    rec = DatasetRecord()
    assert rec.name is None
    assert rec.grant == []
    assert rec.author_persons == []


def test_term_optional_iri():
    t = Term(label="Homo sapiens")
    assert t.iri is None
    assert t.label == "Homo sapiens"
