from __future__ import annotations

from pathlib import Path

from okf_quality.scripts.okf_lint import lint_bundle


def test_niaid_bundle_lint():
    bundle = (
        Path(__file__).resolve().parents[3]
        / "okf"
        / "bundles"
        / "niaid_blueprint"
    )
    if not bundle.is_dir():
        import pytest

        pytest.skip("niaid_blueprint missing")
    findings = lint_bundle(bundle)
    errors = [f for f in findings if f.severity == "error"]
    # Healthy NIAID bundle should have zero structural errors
    assert errors == [], errors
