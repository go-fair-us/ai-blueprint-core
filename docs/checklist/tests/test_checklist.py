"""Checks for the webinar companion checklist.

These tests keep the Markdown source structured enough to filter by
level, keep relative citations resolvable, and catch a few wording
regressions that would re-import known PDF-face errors.
"""

from __future__ import annotations

import hashlib
import re
import sys
import tomllib
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
    "https://www.gofair.us/resources/citation",
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
    assert "https://www.gofair.us/resources/citation" in text
    assert "https://www.gofair.us/citation-recommendations" not in text
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


def test_renderer_does_not_call_date_today():
    assert "date.today" not in Path(build.__file__).read_text(encoding="utf-8")


def test_cli_date_overrides_revision(monkeypatch):
    monkeypatch.delenv("SOURCE_DATE_EPOCH", raising=False)
    revision = build.resolve_revision(cli_date="2026-01-02", source_text=SOURCE.read_text(encoding="utf-8"))
    assert revision.date == "2026-01-02"
    assert revision.date_source == "cli"


def test_source_date_epoch(monkeypatch):
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "1700000000")  # 2023-11-14 UTC
    revision = build.resolve_revision(source_text=SOURCE.read_text(encoding="utf-8"))
    assert revision.date == "2023-11-14"
    assert revision.date_source == "source-date-epoch"


def test_front_matter_date_and_strip():
    raw = "---\nrevision_date: 2026-02-03\n---\n# Title\n\n## Reachable\nintro\n"
    assert build.revision_date_from_front_matter(raw) == "2026-02-03"
    assert not build.strip_front_matter(raw).startswith("---")
    assert build.strip_front_matter(raw).startswith("# Title")


def test_html_relative_links_resolve_from_dist(tmp_path, document, monkeypatch):
    monkeypatch.delenv("SOURCE_DATE_EPOCH", raising=False)
    monkeypatch.setattr(build, "DIST", tmp_path)
    revision = build.Revision("2026-11-06", "testhash", "cli")
    written = build.write_view(document, "all", write_html=True, write_pdf=False, revision=revision)
    html = written["html"].read_text(encoding="utf-8")
    assert "Rendered " not in html
    assert "Checklist source testhash, dated 2026-11-06" in html
    assert 'content="2026-11-06T12:00:00Z"' in html
    assert 'href="style.css"' in html
    assert 'href="../style.css"' not in html
    assert (tmp_path / "style.css").exists()
    urls = re.findall(r'href="([^"]+slideDeckSIReadyRepos\.pdf[^"]*)"', html)
    assert urls
    target = (tmp_path / urls[0].split("#", 1)[0]).resolve()
    assert target.exists(), urls[0]


def test_two_builds_are_reproducible(tmp_path, document, monkeypatch):
    monkeypatch.delenv("SOURCE_DATE_EPOCH", raising=False)
    revision = build.Revision("2026-11-06", "testhash", "cli")
    hashes = []
    texts = []
    for name in ("a", "b"):
        dest = tmp_path / name
        monkeypatch.setattr(build, "DIST", dest)
        written = build.write_view(
            document, "level-1", write_html=True, write_pdf=True, revision=revision
        )
        hashes.append((
            hashlib.sha256(written["html"].read_bytes()).hexdigest(),
            hashlib.sha256(written["pdf"].read_bytes()).hexdigest(),
        ))
        texts.append(written["pdf"].read_bytes())
    assert hashes[0][0] == hashes[1][0]
    if hashes[0][1] != hashes[1][1]:
        # Document metadata-only drift if a future WeasyPrint version introduces it.
        import subprocess
        def pdf_text(data: bytes) -> str:
            path = tmp_path / "cmp.pdf"
            path.write_bytes(data)
            return subprocess.check_output(["pdftotext", "-layout", str(path), "-"], text=True)
        assert pdf_text(texts[0]) == pdf_text(texts[1])
    else:
        assert hashes[0][1] == hashes[1][1]

def test_factcheck_corrections(document):
    by_id = {item.item_id: item for item in document.items}
    assert by_id["MEA-08"].optional
    assert by_id["MEA-08"].title.startswith("Optionally")
    assert by_id["MEA-08"].fields["Kind"] == "advice"
    assert by_id["MEA-08"].fields["Maturity"] == "established"
    assert by_id["RCH-06"].fields["Kind"] == "preference-signal"
    assert by_id["MEA-10"].fields["Kind"] == "advice"
    assert by_id["MEA-07"].fields["Maturity"] == "established"
    assert "If you expose a metadata API" in by_id["CAL-01"].title
    assert "If you expose a metadata API" in by_id["CAL-02"].title
    assert "N/A" in by_id["CAL-01"].body
    assert "N/A" in by_id["CAL-02"].body
    assert "even if you do not operate an API" in by_id["CAL-03"].body
    assert "Do not mark this item N/A solely because you have no API" in by_id["CAL-03"].body
    assert "#page=17" in by_id["RD-03"].fields["Sources"]
    assert "no separate AI-Overviews robots token" in by_id["RCH-03"].body


# Official PEP 723 extractor (https://peps.python.org/pep-0723/).
PEP723_BLOCK_RE = re.compile(
    r"(?m)^# /// (?P<type>[a-zA-Z0-9-]+)$\s(?P<content>(^#(| .*)$\s)+)^# ///$"
)


def read_pep723_script_metadata(source: str) -> dict:
    matches = [m for m in PEP723_BLOCK_RE.finditer(source) if m.group("type") == "script"]
    assert len(matches) == 1, f"expected exactly one PEP 723 script block, found {len(matches)}"
    content = "".join(
        line[2:] if line.startswith("# ") else line[1:]
        for line in matches[0].group("content").splitlines(keepends=True)
    )
    return tomllib.loads(content)


def pins_from_requirements(text: str) -> list[str]:
    pins = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        pins.append(stripped)
    return pins


def test_pep723_pins_match_requirements_txt():
    meta = read_pep723_script_metadata(Path(build.__file__).read_text(encoding="utf-8"))
    reqs = pins_from_requirements((ROOT / "requirements.txt").read_text(encoding="utf-8"))
    assert meta["dependencies"] == reqs
    assert reqs == ["markdown==3.11", "weasyprint==70.0"]
    # Markdown 3.11 requires >=3.11; WeasyPrint 70.0 requires only >=3.10.
    assert meta["requires-python"] == ">=3.11"


def _visible_quickstart_text(text: str) -> str:
    """Link labels only; file paths inside Markdown destinations are ignored."""
    return re.sub(r"\[([^\]]*)\]\([^)]+\)", r"\1", text)


PILLAR_HEADINGS = (
    "## Be Reachable",
    "## Be Readable",
    "## Be Callable",
    "## Be Meaningful",
)


def test_quickstart_has_four_pillar_sections():
    text = build.QUICKSTART.read_text(encoding="utf-8")
    headings = re.findall(r"^## .+", text, flags=re.MULTILINE)
    assert headings == list(PILLAR_HEADINGS)
    first_line = text.lstrip().splitlines()[0]
    assert first_line.startswith("# ")
    assert "five" not in first_line.lower()
    assert "Evaluation" not in headings
    assert not re.search(r"^## .*Evaluation", text, flags=re.MULTILINE | re.IGNORECASE)
    visible = _visible_quickstart_text(text)
    assert "Restricted data should stay protected" in visible
    assert "public descriptive records" in visible
    assert "restricted data download" in visible
    assert "If you already offer a way for software to retrieve data, document it too." in visible
    # This handout no longer advises running evaluations.
    for phrase in (
        "try real questions",
        "outside tools",
        "prompts/evals",
        "competency",
        "AI tool answers",
    ):
        assert phrase.lower() not in visible.lower(), phrase
    words = visible.split()
    assert 400 <= len(words) <= 500, len(words)


def test_quickstart_names_representative_options():
    visible = _visible_quickstart_text(
        build.QUICKSTART.read_text(encoding="utf-8")
    )
    for name in (
        "CDN",
        "robots.txt",
        "rate limits",
        "HTML",
        "sitemap",
        "Signposting",
        "Markdown",
        "llms.txt",
        "OpenAPI",
        "JSON-LD",
        "MCP",
        "DataCite",
        "ORCID",
        "schema.org",
        "SHACL",
        "SSSOM",
    ):
        assert name in visible, name
    assert "optional" in visible.lower()
    assert "proposal" in visible.lower()
    assert "ontology is not required" in visible.lower() or "formal ontology is not required" in visible.lower()
    assert "do not need a new API" in visible or "do not have to launch new services" in visible
    assert "preference" in visible.lower()
    assert "not a guarantee" in visible


def test_quickstart_review_date_fallback_does_not_change_checklist(monkeypatch):
    monkeypatch.delenv("SOURCE_DATE_EPOCH", raising=False)
    monkeypatch.setattr(build, "_git", lambda args: None)
    quick = build.resolve_quickstart_revision()
    assert quick.date == "2026-11-06"
    assert quick.date_source == "review-date"
    checklist = build.resolve_revision(source_text="# Title\n")
    assert checklist.date == "unknown"
    assert checklist.date_source == "unknown"


def test_quickstart_pdf_is_one_page(tmp_path, monkeypatch):
    import subprocess

    monkeypatch.setattr(build, "DIST", tmp_path)
    written = build.write_quickstart(write_html=True, write_pdf=True)
    info = subprocess.check_output(["pdfinfo", str(written["pdf"])], text=True)
    match = re.search(r"^Pages:\s+(\d+)\s*$", info, flags=re.MULTILINE)
    assert match is not None
    assert match.group(1) == "1"
