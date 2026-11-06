"""Checks for the webinar companion checklist.

These tests keep the Markdown source structured enough to filter by
level, keep relative citations resolvable, and catch a few wording
regressions that would re-import known PDF-face errors.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import build  # noqa: E402

SOURCE = ROOT / "checklist.md"

ALLOWED_URL_PREFIXES = (
    "https://openai.com/gptbot.json",
    "https://www.rfc-editor.org/rfc/rfc9309.html",
    "https://developers.google.com/search/docs/crawling-indexing/google-common-crawlers",
    "https://datatracker.ietf.org/doc/html/draft-ietf-aipref-vocab-08",
    "https://datatracker.ietf.org/doc/html/draft-ietf-aipref-attach-05",
    "https://rslstandard.org/rsl",
    "https://sitemaps.org/protocol.html",
    "https://www.sitemaps.org/protocol.html",
    "https://developers.google.com/search/docs/crawling-indexing/robots/robots_txt",
    "https://signposting.org/FAIR/",
    "https://llmstxt.org/",
    "https://developer.chrome.com/docs/lighthouse/agentic-browsing/llms-txt",
    "https://agentskills.io/",
    "https://agenticresourcediscovery.org/spec/",
    "https://agent-plugins.org/",
    "https://github.com/go-fair-us/apireference/",
    "https://doi.org/10.5281/zenodo.17161561",
    "https://www.niaid.nih.gov/research/data-blueprint",
    "https://spec.openapis.org/oas/latest.html",
    "https://www.w3.org/TR/json-ld11/",
    "https://modelcontextprotocol.io/specification/2026-07-28",
    "https://registry.modelcontextprotocol.io/",
    "https://schema.datacite.org/meta/kernel-4.6/",
    "https://bioschemas.org/profiles/Dataset/",
    "https://github.com/NIAID-Data-Ecosystem/nde-schemas",
    "https://spdx.org/licenses/",
    "https://grants.nih.gov/grants/guide/notice-files/NOT-OD-25-081.html",
    "https://credit.niso.org/",
    "https://www.gofair.us/citation-recommendations",
    "https://www.w3.org/TR/prov-o/",
    "https://www.w3.org/community/reports/tdmrep/CG-FINAL-tdmrep-20240510/",
    "https://www.w3.org/TR/shacl/",
    "https://www.w3.org/TR/sparql-rl/",
    "https://mapping-commons.github.io/sssom/",
    "https://data.niaid.nih.gov/knowledge-center/ai-assisted-search",
    "https://example.org/",
)

EXPECTED_IDS = [
    "RCH-01", "RCH-02", "RCH-03", "RCH-04", "RCH-05", "RCH-06", "RCH-07",
    "RD-01", "RD-02", "RD-03", "RD-04", "RD-05", "RD-06", "RD-07", "RD-08",
    "CAL-01", "CAL-02", "CAL-03", "CAL-04", "CAL-05",
    "MEA-01", "MEA-02", "MEA-03", "MEA-04", "MEA-05", "MEA-06", "MEA-07",
    "MEA-08", "MEA-09", "MEA-10",
    "EVL-01", "EVL-02", "EVL-03",
]


@pytest.fixture(scope="module")
def document():
    return build.parse_document(SOURCE.read_text(encoding="utf-8"))


def test_expected_item_ids(document):
    assert [item.item_id for item in document.items] == EXPECTED_IDS


def test_unique_titles(document):
    titles = [item.title for item in document.items]
    assert len(titles) == len(set(titles))


def test_required_narrative_sections(document):
    for item in document.items:
        parts = build.split_body(item.body)
        assert parts["do"], f"{item.item_id} needs Do this"
        assert parts["verify"], f"{item.item_id} needs How to verify"


def test_validator_accepts_source(document):
    assert build.validate_document(document, ROOT) == []


def test_level_filters(document):
    only_one = build.filter_document(document, {1})
    assert only_one.items
    assert all(item.level == 1 for item in only_one.items)
    through_two = build.filter_document(document, {1, 2})
    assert all(item.level in {1, 2} for item in through_two.items)
    assert len(through_two.items) < len(document.items)
    assert len(only_one.items) < len(through_two.items)


def test_relative_links_resolve(document):
    missing = []
    for origin, _label, url in build.extract_links(document):
        if url.startswith(("http://", "https://", "mailto:")):
            continue
        path_part = url.split("#", 1)[0]
        if not path_part:
            continue
        target = (ROOT / path_part).resolve()
        if not target.exists():
            missing.append(f"{origin}: {url}")
    assert missing == []


def test_external_urls_are_allowlisted(document):
    unknown = []
    for origin, _label, url in build.extract_links(document):
        if not url.startswith("http"):
            continue
        if not any(url.startswith(prefix) for prefix in ALLOWED_URL_PREFIXES):
            unknown.append(f"{origin}: {url}")
    assert unknown == []


def test_source_avoids_known_pdf_errors():
    text = SOURCE.read_text(encoding="utf-8")
    assert "draft-ietf-aipref-vocab-08" in text
    assert "draft-ietf-aipref-attach-05" in text
    assert "SSSOM/TSV" in text
    assert "author_id" in text
    assert "protected HTTP" in text
    assert "illustrative" in text
    assert "https://www.w3.org/TR/shacl/" in text
    assert "https://www.w3.org/TR/sparql-rl/" in text
    assert "a certification" in text and "compliance score" in text
    assert "Oct 21" not in text
    assert "public-domain" not in text.lower()
    assert "without manual login" not in text.lower()
    assert "SSSOM/CSV" not in text and "not CSV" in text
    # Preferred citation is vocab-08; -07 may be mentioned only as a stale example.
    if "vocab-07" in text or "vocabulary **-07**" in text:
        assert "follow the glossary" in text or "-08" in text


def test_niaid_data_not_called_public_domain(document):
    mea04 = next(item for item in document.items if item.item_id == "MEA-04")
    blob = mea04.body.lower()
    assert "does **not** assume" in mea04.body or "does not assume" in blob
    assert "public domain" in blob


def test_build_check_exit_code():
    assert build.main(["--check"]) == 0


def test_render_filtered_views(tmp_path, document, monkeypatch):
    monkeypatch.setattr(build, "DIST", tmp_path)
    written = build.write_view(document, "level-1", write_html=True, write_pdf=False)
    html = written["html"].read_text(encoding="utf-8")
    assert "Level 1 view" in html
    assert "RCH-02" in html
    assert "CAL-04" not in html  # level 3 optional MCP
    assert "MEA-08" not in html  # level 3 SHACL
    written_all = build.write_view(document, "all", write_html=True, write_pdf=True)
    pdf = written_all["pdf"]
    assert pdf.exists() and pdf.stat().st_size > 1000
