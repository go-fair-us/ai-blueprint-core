from defs.signatures import ExtractIdentity


def test_identity_signature_forbids_invention():
    assert "Never invent" in (ExtractIdentity.__doc__ or "")
