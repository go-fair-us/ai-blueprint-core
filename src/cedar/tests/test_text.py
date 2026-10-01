from defs.text import clean_iri, clean_literal, normalize_temporal, url_path


def test_clean_literal_strips_wrapping_quotes():
    assert clean_literal('"NCT04640168"') == "NCT04640168"
    assert clean_literal("'Adaptive COVID-19 Treatment Trial 4 (ACTT-4)'") == (
        "Adaptive COVID-19 Treatment Trial 4 (ACTT-4)"
    )
    assert clean_literal('""NCT04640168""') == "NCT04640168"


def test_clean_literal_none_placeholders():
    assert clean_literal("None") is None
    assert clean_literal("null") is None
    assert clean_literal("") is None
    assert clean_literal(None) is None


def test_clean_iri_rejects_none():
    assert clean_iri("None") is None
    assert clean_iri("https://ror.org/043z4tv69") == "https://ror.org/043z4tv69"


def test_normalize_temporal_month_only():
    assert normalize_temporal("2020-11") == "2020-11-01T00:00:00"
    assert normalize_temporal("2020-11T00:00:00") == "2020-11-01T00:00:00"
    assert "T" in (normalize_temporal("2020-11-24") or "")
    assert normalize_temporal("2020-11-24T00:00:00") == "2020-11-24T00:00:00"


def test_url_path():
    assert (
        url_path(
            "https://accessclinicaldata.niaid.nih.gov/api/files/NCT04640168/ACTT-4_Data_Use_Limitations.pdf"
        )
        == "/api/files/NCT04640168/ACTT-4_Data_Use_Limitations.pdf"
    )
