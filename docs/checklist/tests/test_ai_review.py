"""Checks for the AI review companion mapping and start block."""

from __future__ import annotations

import hashlib
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

CHECKLIST_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
AI_REVIEW = CHECKLIST_DIR / "ai-review.md"
CHECKLIST = CHECKLIST_DIR / "checklist.md"
EVALS_DIR = REPO_ROOT / "prompts" / "evals"

sys.path.insert(0, str(CHECKLIST_DIR))
import build  # noqa: E402

PINNED_SHA = "f0a7198e0fea7b4d16a5d5fc7bfa3e115c052973"
CHECKLIST_SHA = "c7053c04d88eed8013ec052ab61bbccbaf5b3917"
BRANCH = "docs/webinar-nov2026-repository-checklist"
COMPANION_RAW = (
    "https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/"
    f"{BRANCH}/docs/checklist/ai-review.md"
)
TREE_EVALS = (
    "https://github.com/go-fair-us/ai-blueprint-core/tree/"
    f"{PINNED_SHA}/prompts/evals"
)
CATALOG = (
    "https://github.com/go-fair-us/ai-blueprint-core/blob/"
    f"{PINNED_SHA}/docs/evalPrompts.md"
)
CHECKLIST_BLOB = (
    "https://github.com/go-fair-us/ai-blueprint-core/blob/"
    f"{CHECKLIST_SHA}/docs/checklist/checklist.md"
)
CHECKLIST_RAW = (
    "https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/"
    f"{CHECKLIST_SHA}/docs/checklist/checklist.md"
)
RAW_RE = re.compile(
    r"https://raw\.githubusercontent\.com/go-fair-us/ai-blueprint-core/"
    + PINNED_SHA
    + r"/prompts/evals/([A-Za-z0-9-]+)\.md"
)
ROW_RE = re.compile(
    r"^\| (?P<id>(?:RCH|RD|CAL|MEA|EVL)-\d{2}) \| "
    r"(?P<coverage>eval|partial|manual) \| "
    r"(?P<prompts>.*?) \| (?P<capabilities>.*?) \| (?P<notes>.*?) \|\s*$",
    re.M,
)
MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
AUTO_LINK_RE = re.compile(r"<(https?://[^>]+)>")
RAW_DIR_RE = re.compile(
    r"https://raw\.githubusercontent\.com/go-fair-us/ai-blueprint-core/"
    r"[^/\s)]+/prompts/evals/?$"
)

ALLOWED_EVAL_FOR_ID = {
    "RCH-02": {"robots-policy"},
    "RCH-03": {"robots-policy"},
    "RD-01": {"sitemap"},
    "RD-02": {"server-rendered-content"},
    "RD-03": {"markdown-negotiation"},
    "RD-05": {"llms-txt"},
    "RD-06": {"agent-documentation"},
    "CAL-01": {"openapi-discovery"},
    "CAL-02": {"metadata-api", "api-http-behavior"},
    "CAL-03": {"dataset-jsonld"},
    "CAL-04": {"mcp-exposure"},
    "MEA-01": {"persistent-identifiers"},
    "MEA-02": {"vocabulary"},
    "MEA-03": {"metadata-profile"},
    "MEA-04": {"rights-and-license"},
    "MEA-05": {"citation"},
    "MEA-06": {"provenance-lineage"},
    "MEA-08": {"shacl-shapes"},
    "MEA-10": {"sssom-mappings"},
}

MANUAL_IDS = {
    "RCH-01",
    "RCH-04",
    "RCH-05",
    "RCH-06",
    "RCH-07",
    "RD-04",
    "RD-07",
    "RD-08",
    "CAL-05",
    "MEA-07",
    "MEA-09",
    "EVL-01",
    "EVL-02",
    "EVL-03",
}

PARTIAL_IDS = {"MEA-08"}

UNSUPPORTED_FORCED = {
    "RCH-01": {"reachable-fetch"},
    "RCH-04": {"robots-policy"},
    "RCH-06": {"robots-policy"},
    "RD-08": {"agent-documentation"},
    "CAL-05": {"mcp-exposure"},
    "MEA-07": {"robots-policy"},
    "MEA-09": {"shacl-shapes"},
    "EVL-01": {"competency-answerability", "competency-questions"},
    "EVL-02": {"competency-answerability"},
}

REQUIRED_CAP_TOKENS = {
    "RCH-01": {"operator", "manual"},
    "RCH-02": {"public-fetch", "status", "raw-headers", "raw-body"},
    "RCH-03": {"public-fetch", "status", "raw-headers", "raw-body"},
    "RCH-04": {"operator", "manual"},
    "RCH-05": {"operator", "manual"},
    "RCH-06": {"operator", "manual"},
    "RCH-07": {"operator", "manual"},
    "RD-01": {"public-fetch", "status", "raw-headers", "raw-body"},
    "RD-02": {"public-fetch", "status", "raw-headers", "raw-body"},
    "RD-03": {"public-fetch", "status", "raw-headers", "raw-body", "set-Accept"},
    "RD-04": {"manual"},
    "RD-05": {"public-fetch", "status", "raw-headers", "raw-body"},
    "RD-06": {"public-fetch", "status", "raw-headers", "raw-body", "optional-render"},
    "RD-07": {"manual"},
    "RD-08": {"manual"},
    "CAL-01": {"public-fetch", "status", "raw-headers", "raw-body", "optional-render"},
    "CAL-02": {"public-fetch", "status", "raw-headers", "raw-body", "set-Accept"},
    "CAL-03": {"public-fetch", "status", "raw-headers", "raw-body", "script-elements"},
    "CAL-04": {"public-fetch", "status", "raw-headers", "raw-body", "no-MCP-calls"},
    "CAL-05": {"operator", "manual"},
    "MEA-01": {"public-fetch", "status", "raw-headers", "raw-body", "optional-HEAD"},
    "MEA-02": {"public-fetch", "status", "raw-headers", "raw-body", "optional-render"},
    "MEA-03": {"public-fetch", "status", "raw-headers", "raw-body", "Link-header"},
    "MEA-04": {"public-fetch", "status", "raw-headers", "raw-body"},
    "MEA-05": {"public-fetch", "status", "raw-headers", "raw-body", "optional-render"},
    "MEA-06": {"public-fetch", "status", "raw-headers", "raw-body"},
    "MEA-07": {"manual"},
    "MEA-08": {"public-fetch", "status", "raw-headers", "raw-body", "no-validator"},
    "MEA-09": {"manual"},
    "MEA-10": {"public-fetch", "status", "raw-headers", "raw-body", "optional-render"},
    "EVL-01": {"manual"},
    "EVL-02": {"manual"},
    "EVL-03": {"manual"},
}


def _text() -> str:
    return AI_REVIEW.read_text(encoding="utf-8")


def _without_fences(text: str) -> str:
    return re.sub(r"```.*?```", "", text, flags=re.S)


def _checklist_ids() -> list[str]:
    doc = build.parse_document(CHECKLIST.read_text(encoding="utf-8"))
    return [item.item_id for item in doc.items]


def _mapping_rows() -> list[dict]:
    rows = []
    for match in ROW_RE.finditer(_text()):
        prompts = RAW_RE.findall(match.group("prompts"))
        caps = {
            token.strip()
            for token in match.group("capabilities").split(";")
            if token.strip()
        }
        rows.append(
            {
                "id": match.group("id"),
                "coverage": match.group("coverage"),
                "prompts": prompts,
                "capabilities": caps,
                "notes": match.group("notes").strip(),
            }
        )
    return rows


def _markdown_links(text: str) -> list[tuple[str, str]]:
    return MD_LINK_RE.findall(_without_fences(text))


def test_mapping_covers_all_checklist_ids_exactly_once() -> None:
    expected = _checklist_ids()
    rows = _mapping_rows()
    found = [row["id"] for row in rows]
    assert len(expected) == 33
    assert found == expected
    assert len(found) == len(set(found)) == 33
    coverage = {row["id"]: row["coverage"] for row in rows}
    assert sum(1 for value in coverage.values() if value == "eval") == 18
    assert sum(1 for value in coverage.values() if value == "partial") == 1
    assert sum(1 for value in coverage.values() if value == "manual") == 14


def test_pinned_eval_paths_are_valid_local_files() -> None:
    rows = _mapping_rows()
    seen = []
    for row in rows:
        for name in row["prompts"]:
            path = EVALS_DIR / f"{name}.md"
            assert path.is_file(), f"missing local eval file for {row['id']}: {path}"
            seen.append(name)
    assert seen, "expected at least one pinned eval URL"
    table_rows = "\n".join(
        line for line in _text().splitlines() if ROW_RE.match(line)
    )
    stray = re.findall(
        r"https://(?:raw\.)?github(?:usercontent)?\.com/[^\s)<]+",
        table_rows,
    )
    for url in stray:
        assert RAW_RE.fullmatch(url), f"unpinned or unexpected URL in mapping table: {url}"


def test_coverage_matches_allowed_mappings_and_manual_gaps() -> None:
    rows = {row["id"]: row for row in _mapping_rows()}
    expected = set(_checklist_ids())
    assert set(ALLOWED_EVAL_FOR_ID) | MANUAL_IDS == expected
    assert not (set(ALLOWED_EVAL_FOR_ID) & MANUAL_IDS)
    assert "RCH-06" in MANUAL_IDS
    assert "RCH-06" not in ALLOWED_EVAL_FOR_ID

    for item_id, allowed in ALLOWED_EVAL_FOR_ID.items():
        row = rows[item_id]
        wanted = "partial" if item_id in PARTIAL_IDS else "eval"
        assert row["coverage"] == wanted, item_id
        assert set(row["prompts"]) == allowed, item_id
        assert row["notes"], item_id

    for item_id in MANUAL_IDS:
        row = rows[item_id]
        assert row["coverage"] == "manual", item_id
        assert row["prompts"] == [], f"{item_id} should not force an eval URL"
        assert row["notes"], f"{item_id} needs an explicit manual-gap reason"


def test_no_unsupported_forced_mapping() -> None:
    rows = {row["id"]: row for row in _mapping_rows()}
    for item_id, forbidden in UNSUPPORTED_FORCED.items():
        found = set(rows[item_id]["prompts"])
        overlap = found & forbidden
        assert not overlap, f"{item_id} forced unsupported mapping(s): {overlap}"
        assert rows[item_id]["coverage"] == "manual"


def test_capability_column_matches_prompt_needs() -> None:
    rows = {row["id"]: row for row in _mapping_rows()}
    assert set(REQUIRED_CAP_TOKENS) == set(rows)
    for item_id, required in REQUIRED_CAP_TOKENS.items():
        missing = required - rows[item_id]["capabilities"]
        assert not missing, f"{item_id} missing capability tokens: {missing}"
        assert rows[item_id]["capabilities"], item_id


def test_high_risk_rows_state_residual_gaps() -> None:
    notes = {row["id"]: row["notes"] for row in _mapping_rows()}
    assert "SKILL.md" in notes["RD-06"] or "skill-md" in notes["RD-06"]
    assert "initial-HTML" in notes["CAL-03"]
    assert "API JSON-LD" in notes["CAL-03"] or "profile" in notes["CAL-03"]
    assert notes["CAL-04"].startswith("Discovery only")
    assert "security" in notes["CAL-04"]
    assert "Identifier forms" in notes["MEA-01"]
    assert "resolution" in notes["MEA-01"]
    assert "Declaration discovery" in notes["MEA-03"]
    assert "conformance" in notes["MEA-03"]
    assert "presence" in notes["MEA-04"]
    assert "legal" in notes["MEA-04"]
    assert "Citation-pattern" in notes["MEA-05"] or "creator discovery" in notes["MEA-05"]
    assert "checksum" in notes["MEA-06"]
    assert "Content-Signals" in notes["RCH-06"]
    assert "Content-Usage" in notes["RCH-06"]
    assert "AIPREF" in notes["RCH-06"]
    text = _text()
    assert "does not validate scientific correctness" in text
    assert "Answerability is not scientific correctness" in text


def test_start_block_is_self_contained_single_run() -> None:
    text = _text()
    start = text.split("```text", 1)[1].split("```", 1)[0]
    assert f"COMPANION={COMPANION_RAW}" in start
    assert "DOMAIN=https://YOUR-PUBLIC-SITE.example/" in start
    assert "SELECTED_IDS=RD-01" in start
    assert "SELECTED_IDS=RD-01,RD-02,MEA-05" not in text
    assert "PROMPT_REVISION=" + PINNED_SHA in start
    assert f"CHECKLIST_SOURCE={CHECKLIST_RAW}" in start
    assert "trusted routing context" in start
    assert "Fetch that row's pinned prompt file" in start
    assert "Return evidence using the companion schema" in start
    assert "Then stop" in start
    assert "Do not run another ID in this ordinary chat" in start
    for phrase in (
        "Raw status code",
        "Response headers",
        "Unmodified body",
        "script elements",
        "Operator evidence",
    ):
        assert phrase in start, phrase
    assert "paste this entire companion" in text.lower()
    assert "harness that truly isolates" in text.lower()
    assert "sitemap.md" in start
    assert "checklist_assessment" in text


def test_evidence_schema_separates_prompt_and_checklist() -> None:
    text = _text()
    schema = text.split("```yaml", 1)[1].split("```", 1)[0]
    assert "Illustrative example only" in schema
    for field in (
        "item_id",
        "applicable",
        "n_a_reason",
        "run_status",
        "prompt_file",
        "prompt_revision",
        "prompt_file_url",
        "fetched_status",
        "prompt_verdict",
        "checks",
        "checklist_assessment",
        "unchecked_aspects",
        "human_follow_up",
        "evidence_kind",
        "url",
        "evaluated_at",
        "observation",
        "limits",
        "next_action",
    ):
        assert f"{field}:" in schema, field
    assert "never inferred from prompt_verdict" in schema
    assert "illustrative timestamp, not an observation" in schema
    assert "unassessed" in schema
    for verdict in ("present", "partial", "absent", "blocked", "not-observable"):
        assert verdict in schema
    assert "does not complete a checklist item" in text
    assert "not that a public artifact is missing everywhere" in text
    assert "numeric score" in text.lower() or "do not invent a numeric score" in text.lower()


def test_safety_and_known_pitfalls_are_explicit() -> None:
    text = _text()
    assert "HTTP 429" in text
    assert "does **not** mean there is no rate limiting" in text
    assert "cause a 429" in text
    assert "not compliance" in text
    assert "bundled starter" in text
    assert "SPARQL RL" in text
    assert "SRL" in text
    assert "not MCP tools" in text
    assert "You do not need a new MCP server" in text
    assert "untrusted" in text.lower()
    assert "not instructions" in text.lower()
    assert "controlled" in text.lower()
    assert "A link is not a tool" in text
    assert "not a recommendation to remove necessary protections" in text


def test_markdown_links_are_descriptive_and_destinations_work() -> None:
    text = _text()
    prose = _without_fences(text)
    autos = AUTO_LINK_RE.findall(prose)
    assert autos == [], f"use descriptive Markdown links, not autolinks: {autos}"
    dirs = RAW_DIR_RE.findall(prose) + RAW_DIR_RE.findall(text)
    assert dirs == [], f"raw GitHub does not serve directories: {dirs}"
    links = _markdown_links(text)
    assert links, "expected descriptive Markdown links"
    hrefs = []
    for label, href in links:
        assert label.strip(), f"empty link text for {href}"
        assert label.strip() != href, f"link text should describe destination: {href}"
        hrefs.append(href)
    assert TREE_EVALS in hrefs
    assert CATALOG in hrefs
    assert CHECKLIST_BLOB in hrefs
    assert CHECKLIST_RAW in hrefs
    assert any(href.endswith("/prompts/evals/sitemap.md") for href in hrefs)

    seen: dict[str, bytes] = {}
    for href in sorted(set(hrefs)):
        req = urllib.request.Request(
            href,
            headers={"User-Agent": "ai-blueprint-core-checklist-link-check"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read()
                status = resp.status
        except urllib.error.HTTPError as exc:
            raise AssertionError(f"{href} returned HTTP {exc.code}") from exc
        assert status == 200, f"{href} returned HTTP {status}"
        seen[href] = body
        match = RAW_RE.fullmatch(href)
        if match:
            local = (EVALS_DIR / f"{match.group(1)}.md").read_bytes()
            assert body == local, f"{href} bytes differ from local file"

    checklist_body = seen[CHECKLIST_RAW]
    # The published pin is the last pushed checklist; local file should match
    # unless later uncommitted checklist edits appear.
    local_checklist = CHECKLIST.read_bytes()
    assert hashlib.sha256(checklist_body).digest() == hashlib.sha256(local_checklist).digest()
