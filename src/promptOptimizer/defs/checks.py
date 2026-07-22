"""Reusable, LM-free scoring primitives shared across every task.

These are pure functions over the generated text — no LLM calls. Tasks compose
them (with their own weights) in ``tasks.base.score_artifact``.

Checks are intentionally strict so baseline scores leave headroom for optimizers:
Table 1 needs non-empty keys *and* Blueprint-default value formats; OpenAPI is
graded for structure *and* scenario relevance; filler/template answers and
wrong schema.org field names are penalized.
"""
from __future__ import annotations

import json
import re
from typing import Any

import yaml

# Blueprint Table 1 metadata elements — the authoritative schema.org property
# names from NIAID_Blueprint_v2 §1.2 Table 1. Note: the Blueprint uses
# `author`/`dateCreated`/`funder`/`grant` (NOT creator/datePublished/funding).
# infectiousAgent/host/healthCondition are the IID-domain fields. Reconcile
# here if the spec's Table 1 changes.
TABLE1_ELEMENTS = [
    "type", "identifier", "name", "description", "dateCreated", "author",
    "funder", "grant", "measurementTechnique", "distribution", "citation",
    "infectiousAgent", "host", "healthCondition", "conditionsOfAccess",
    "license", "spatialCoverage", "temporalCoverage",
]

# ORCID: classic 0000-000X-… range plus the modern 0009-… registrant block.
_PID_PATTERNS = {
    "DOI": re.compile(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+"),
    "ORCID": re.compile(
        r"(?:0000-000[0-9]|0009-[0-9]{4})-[0-9]{4}-[0-9]{3}[0-9X]"
    ),
    "ROR": re.compile(r"ror\.org/0[a-hj-km-np-tv-z0-9]{8}"),
    "RRID": re.compile(r"RRID:\s?(?:SCR|AB|CVCL|IMSR|Addgene)_\S+"),
}

# Field scopes where each PID type is expected under the Blueprint defaults.
_PID_FIELDS = {
    "DOI": ("identifier",),
    "ORCID": ("author",),
    "ROR": ("funder",),
    "RRID": (),  # no single required field; full-document search is fine
}

# Blueprint-preferred value shapes (any match in the field's serialized text).
_FIELD_FORMATS: dict[str, tuple[re.Pattern[str], str]] = {
    "identifier": (
        re.compile(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+|doi\.org/10\."),
        "expected a resolvable DOI",
    ),
    "author": (
        re.compile(r"(?:0000-000[0-9]|0009-[0-9]{4})-[0-9]{4}-[0-9]{3}[0-9X]"),
        "expected an ORCID",
    ),
    "funder": (
        re.compile(r"ror\.org/0[a-hj-km-np-tv-z0-9]{8}"),
        "expected a ROR id",
    ),
    "dateCreated": (
        re.compile(r"\b\d{4}-\d{2}-\d{2}\b|\b\d{4}-\d{2}\b|\b\d{4}\b"),
        "expected ISO 8601-ish date (YYYY-MM-DD)",
    ),
    "measurementTechnique": (
        re.compile(r"NCIT_?[A-Z]?\d+|purl\.obolibrary\.org/obo/NCIT_|ncit\.nci\.nih\.gov", re.I),
        "expected an NCIT term/IRI",
    ),
    "infectiousAgent": (
        re.compile(r"NCBITaxon_?\d+|purl\.obolibrary\.org/obo/NCBITaxon_", re.I),
        "expected an NCBITaxon term/IRI",
    ),
    "host": (
        re.compile(r"NCBITaxon_?\d+|purl\.obolibrary\.org/obo/NCBITaxon_", re.I),
        "expected an NCBITaxon term/IRI",
    ),
    "healthCondition": (
        re.compile(r"MONDO_?\d+|purl\.obolibrary\.org/obo/MONDO_", re.I),
        "expected a MONDO term/IRI",
    ),
    "license": (
        re.compile(
            r"spdx\.org/licenses/|creativecommons\.org/licenses/|"
            r"\b(CC-BY|CC0|MIT|Apache-2\.0|GPL-3\.0)\b",
            re.I,
        ),
        "expected an SPDX id/URL or common open license URI",
    ),
    "spatialCoverage": (
        re.compile(
            r"\b[A-Z]{2}\b|schema\.org/(Country|Place|AdministrativeArea)|"
            r"iso\.org/obp/ui/#iso:std:iso:3166",
            re.I,
        ),
        "expected ISO 3166 code or Place/Country structure",
    ),
    "temporalCoverage": (
        re.compile(r"\d{4}(-\d{2}(-\d{2})?)?(/\d{4}(-\d{2}(-\d{2})?)?)?"),
        "expected ISO 8601 date or interval",
    ),
    "grant": (
        re.compile(r"[A-Z0-9][A-Z0-9\-/.]{4,}", re.I),
        "expected an alphanumeric grant id",
    ),
    "citation": (
        re.compile(r"https?://|doi\.org/|10\.\d{4,9}/"),
        "expected an IRI/URL or DOI",
    ),
    "distribution": (
        re.compile(r"https?://"),
        "expected a URL (contentUrl / distribution IRI)",
    ),
    "conditionsOfAccess": (
        re.compile(r"https?://|open|restricted|controlled|embargo", re.I),
        "expected an access URL or access category",
    ),
}

# Present-but-wrong-format still earns partial credit (key is there).
_FORMAT_FAIL_CREDIT = 0.30

_CODE_BLOCK = re.compile(r"```([\w+-]*)\n(.*?)```", re.DOTALL)
_PLACEHOLDER = re.compile(
    r"^(xxx+|n/?a|tbd|todo|placeholder|example(\s+value)?|string|null|none"
    r"|\.\.\.|…|your\s+\w+|insert\s+\w+)$",
    re.I,
)
_HTTP_METHODS = frozenset({"get", "post", "put", "patch", "delete", "head", "options"})

# Generic template tells that inflate scores without scenario grounding.
_FILLER_PATTERNS = [
    (re.compile(r"\bexample dataset\b", re.I), "generic 'example dataset' name/text"),
    (re.compile(r"\bsample (data|dataset|repository)\b", re.I), "generic 'sample …' wording"),
    (re.compile(r"\bjohn doe\b|\bjane doe\b", re.I), "placeholder person name"),
    (re.compile(r"\blorem ipsum\b", re.I), "lorem ipsum filler"),
    (re.compile(r"\b(foo|bar|baz)\b", re.I), "foo/bar/baz placeholder token"),
    (re.compile(r"example\.(org|com)", re.I), "example.org/com placeholder host"),
    (re.compile(r"\bTODO\b|\bTBD\b|\bxxx+\b", re.I), "TODO/TBD/xxx placeholder"),
    (re.compile(r"\bdataset name\b|\binsert (name|description|value)\b", re.I), "instructional placeholder text"),
]

# Blueprint forbids these schema.org alternatives for Table 1.
_WRONG_FIELD_NAMES = ("creator", "datePublished", "funding", "datePublished")

_STOPWORDS = frozenset(
    """
    a an the and or of to for in on with by from that this these those is are was
    were be been being it its as at into about over under after before between
    their its our your they them we us you i via per using use used needs need
    want wants should must can may will would could about across each all any
    data dataset datasets repository resource api metadata machine readable
    json ld openapi endpoint endpoints expose return returns provide access
    """.split()
)


def code_blocks(text: str) -> list[tuple[str, str]]:
    """Return (language, body) pairs for every fenced code block."""
    return [(lang.lower(), body) for lang, body in _CODE_BLOCK.findall(text or "")]


def find_jsonld(blocks) -> dict | None:
    """First code block that parses as a JSON object containing ``@context``."""
    for lang, body in blocks:
        if lang in ("json", "jsonld", "json-ld", ""):
            try:
                obj = json.loads(body)
            except Exception:
                continue
            if isinstance(obj, dict) and "@context" in obj:
                return obj
    return None


def find_openapi(blocks) -> dict | None:
    """First code block that parses (YAML/JSON) and looks like an OpenAPI doc."""
    for lang, body in blocks:
        if lang in ("yaml", "yml", "json", "openapi", ""):
            try:
                obj = yaml.safe_load(body)  # YAML is a JSON superset
            except Exception:
                continue
            if isinstance(obj, dict) and ("openapi" in obj or "swagger" in obj or "paths" in obj):
                return obj
    return None


def _nonempty_value(v: Any) -> bool:
    """True if ``v`` carries real content (not null/empty/placeholder)."""
    if v is None:
        return False
    if isinstance(v, bool):
        return True
    if isinstance(v, (int, float)):
        return True
    if isinstance(v, str):
        s = v.strip()
        return bool(s) and _PLACEHOLDER.match(s) is None
    if isinstance(v, list):
        return any(_nonempty_value(x) for x in v)
    if isinstance(v, dict):
        return any(_nonempty_value(x) for x in v.values())
    return True


def _element_present(obj: Any, name: str) -> bool:
    """True if ``name`` appears as a JSON key with a non-empty value.

    For Table 1's ``type`` element, accepts either ``@type`` or ``type``.
    Walks nested objects/arrays so properties nested under e.g. ``about`` still
    count — but free text outside the JSON-LD never does.
    """
    keys = ("@type", "type") if name == "type" else (name,)

    def walk(node: Any) -> bool:
        if isinstance(node, dict):
            for k in keys:
                if k in node and _nonempty_value(node[k]):
                    return True
            return any(walk(v) for v in node.values())
        if isinstance(node, list):
            return any(walk(x) for x in node)
        return False

    return walk(obj)


def _field_text(obj: Any, *names: str) -> str:
    """Concatenate string forms of values under the given property names."""
    if not names or obj is None:
        return ""
    want = set(names)
    parts: list[str] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                if k in want or k.lstrip("@") in want:
                    parts.append(v if isinstance(v, str) else json.dumps(v, default=str))
                walk(v)
        elif isinstance(node, list):
            for x in node:
                walk(x)

    walk(obj)
    return "\n".join(parts)


def _format_ok(element: str, jsonld: dict) -> tuple[bool | None, str]:
    """Return (True/False/None, note). None means no format constraint for this element."""
    spec = _FIELD_FORMATS.get(element)
    if spec is None:
        return None, ""
    pat, msg = spec
    text = _field_text(jsonld, element if element != "type" else "@type", element)
    if not text.strip():
        return False, msg
    if pat.search(text):
        return True, ""
    return False, msg


def table1_coverage(jsonld: dict | None, raw: str = "") -> tuple[float, list[str]]:
    """Table 1 score in ``[0, 1]``: presence × correct Blueprint value formats.

    Missing element → 0. Present with no format rule → 1. Present but wrong
    format → partial credit. Free-text matching is never used.
    """
    del raw  # free-text fallback removed on purpose
    if not jsonld:
        return 0.0, list(TABLE1_ELEMENTS)

    missing: list[str] = []
    notes: list[str] = []
    scores: list[float] = []
    for e in TABLE1_ELEMENTS:
        if not _element_present(jsonld, e):
            missing.append(e)
            scores.append(0.0)
            continue
        ok, msg = _format_ok(e, jsonld)
        if ok is None or ok:
            scores.append(1.0)
        else:
            scores.append(_FORMAT_FAIL_CREDIT)
            notes.append(f"{e} ({msg})")

    # Encode format failures into the missing list for feedback readability.
    if notes:
        missing = missing + [f"~format: {n}" for n in notes]
    return sum(scores) / len(TABLE1_ELEMENTS), missing


def jsonld_score(jsonld: dict | None) -> tuple[float, list[str]]:
    """Graded JSON-LD quality in ``[0, 1]`` plus human-readable notes."""
    if not jsonld:
        return 0.0, ["no parseable JSON-LD block with @context in a fenced code block"]

    notes: list[str] = []
    score = 0.0

    # Max 1.0 when fully correct: context 0.35 + type 0.25 + identifier 0.20 + name 0.20.
    score += 0.20
    ctx_s = json.dumps(jsonld.get("@context")).lower()
    if "schema.org" in ctx_s:
        score += 0.15
    else:
        notes.append("@context does not reference schema.org")

    t = jsonld.get("@type", jsonld.get("type"))
    if _nonempty_value(t):
        score += 0.10
        types = t if isinstance(t, list) else [t]
        if any(str(x).rsplit("/", 1)[-1].lower() == "dataset" for x in types):
            score += 0.15
        else:
            notes.append("@type is not Dataset")
    else:
        notes.append("missing @type / type")

    if _element_present(jsonld, "identifier"):
        # Prefer a real DOI, not just any non-empty string.
        ok, _ = _format_ok("identifier", jsonld)
        score += 0.20 if ok else 0.08
        if not ok:
            notes.append("identifier present but not a DOI")
    else:
        notes.append("missing non-empty identifier")

    if _element_present(jsonld, "name"):
        name = str(jsonld.get("name", "")).strip().lower()
        if name in {"dataset", "example", "sample", "example dataset", "my dataset", "test"}:
            score += 0.06
            notes.append("name is too generic")
        else:
            score += 0.20
    else:
        notes.append("missing non-empty name")

    # Penalize Blueprint-discouraged field names when they appear as keys.
    wrong = [k for k in _WRONG_FIELD_NAMES if _has_key(jsonld, k)]
    if wrong:
        score = max(0.0, score - 0.15 * len(set(wrong)))
        notes.append("wrong field names (use author/dateCreated/funder+grant): " + ", ".join(sorted(set(wrong))))

    return min(1.0, score), notes


def _has_key(obj: Any, name: str) -> bool:
    if isinstance(obj, dict):
        if name in obj:
            return True
        return any(_has_key(v, name) for v in obj.values())
    if isinstance(obj, list):
        return any(_has_key(x, name) for x in obj)
    return False


def _scenario_tokens(task_description: str) -> list[str]:
    words = re.findall(r"[a-z][a-z0-9\-]{3,}", (task_description or "").lower())
    # Preserve order, drop stopwords/dupes.
    seen: set[str] = set()
    out: list[str] = []
    for w in words:
        if w in _STOPWORDS or w in seen:
            continue
        seen.add(w)
        out.append(w)
    return out


def openapi_score(
    openapi: dict | None,
    task_description: str = "",
) -> tuple[float, list[str]]:
    """Graded OpenAPI quality: structure (65%) + scenario path relevance (35%)."""
    if not openapi:
        return 0.0, ["no parseable OpenAPI/Swagger document in a fenced code block"]

    notes: list[str] = []
    structure = 0.0

    if "openapi" in openapi or "swagger" in openapi:
        structure += 0.25
    else:
        notes.append("missing openapi/swagger version field")

    paths = openapi.get("paths")
    has_op = False
    has_resp = False
    if isinstance(paths, dict) and paths:
        structure += 0.35
        for item in paths.values():
            if not isinstance(item, dict):
                continue
            for method, op in item.items():
                if method.lower() not in _HTTP_METHODS or not isinstance(op, dict):
                    continue
                has_op = True
                if "responses" in op:
                    has_resp = True
        if has_op:
            structure += 0.20
        else:
            notes.append("paths has no HTTP operations (get/post/...)")
        if has_resp:
            structure += 0.20
        else:
            notes.append("operations missing responses")
    else:
        notes.append("missing or empty paths")
        paths = {}

    structure = min(1.0, structure)

    # Scenario relevance: path/method text should share tokens with the scenario.
    relevance = 0.0
    tokens = _scenario_tokens(task_description)
    if isinstance(paths, dict) and paths and tokens:
        path_blob = " ".join(str(p) for p in paths.keys()).lower()
        path_blob += " " + json.dumps(paths, default=str).lower()
        hits = [t for t in tokens if t in path_blob]
        # Need meaningful overlap; reward denser matches up to 1.0.
        relevance = min(1.0, len(hits) / max(3, min(8, len(tokens))))
        if relevance < 0.34:
            notes.append(
                "OpenAPI paths look generic / weakly tied to the scenario "
                f"(matched: {', '.join(hits[:6]) or 'none'})"
            )
        # Bonus signal: common access verbs present when scenario asks for them.
        intent = {
            "search": any(t in tokens for t in ("search", "filter", "query", "find")),
            "bulk": any(t in tokens for t in ("bulk", "list", "listing", "catalog")),
            "doi": any(t in tokens for t in ("doi", "identifier", "pid", "resolve", "resolution")),
            "metadata": any(t in tokens for t in ("metadata", "json-ld", "jsonld", "schema")),
        }
        intent_hits = 0
        intent_need = 0
        for key, needed in intent.items():
            if not needed:
                continue
            intent_need += 1
            if key in path_blob or (key == "doi" and "identifier" in path_blob):
                intent_hits += 1
        if intent_need:
            relevance = min(1.0, 0.7 * relevance + 0.3 * (intent_hits / intent_need))
    elif task_description and not paths:
        notes.append("cannot judge path relevance without paths")
    else:
        # No scenario text (shouldn't happen in this harness) — don't punish.
        relevance = structure

    score = 0.65 * structure + 0.35 * relevance
    return min(1.0, score), notes


def pid_score(raw: str, jsonld: dict | None = None) -> tuple[float, list[str]]:
    """Score persistent-identifier usage; prefer Blueprint-expected fields."""
    raw = raw or ""
    full = (json.dumps(jsonld) if jsonld else "") + "\n" + raw
    found: list[str] = []
    credit = 0.0
    weights = {"DOI": 0.4, "ORCID": 0.2, "ROR": 0.2, "RRID": 0.2}

    for name, weight in weights.items():
        pat = _PID_PATTERNS[name]
        fields = _PID_FIELDS[name]
        if jsonld is not None and fields:
            scoped = _field_text(jsonld, *fields)
            if pat.search(scoped):
                found.append(name)
                credit += weight
            elif pat.search(full):
                found.append(f"{name} (not in {'/'.join(fields)})")
                credit += weight * 0.5
        else:
            if pat.search(full):
                found.append(name)
                credit += weight

    return min(1.0, credit), found


def content_quality(text: str, jsonld: dict | None = None) -> tuple[float, list[str]]:
    """Penalize template filler and Blueprint-wrong field names. Returns ``[0, 1]``.

    Multiplied into the weighted score so a perfectly structured but generic
    "Example Dataset / John Doe / example.org" answer cannot sit near 1.0.
    """
    blob = (text or "") + "\n" + (json.dumps(jsonld, default=str) if jsonld else "")
    penalty = 0.0
    notes: list[str] = []

    for pat, label in _FILLER_PATTERNS:
        if pat.search(blob):
            penalty += 0.12
            notes.append(label)

    wrong = [k for k in sorted(set(_WRONG_FIELD_NAMES)) if _has_key(jsonld, k)] if jsonld else []
    # Also catch wrong names only in prose/code outside parsed JSON-LD.
    for k in sorted(set(_WRONG_FIELD_NAMES)):
        if k not in wrong and re.search(rf'"{k}"\s*:', blob):
            wrong.append(k)
    if wrong:
        penalty += 0.15 * len(wrong)
        notes.append("wrong field names: " + ", ".join(wrong))

    if jsonld is not None:
        name = str(jsonld.get("name") or "").strip().lower()
        if name in {"dataset", "example", "sample", "example dataset", "my dataset", "test dataset", "test"}:
            penalty += 0.10
            notes.append("generic dataset name")
        desc = str(jsonld.get("description") or "")
        if desc and len(desc.strip()) < 40:
            penalty += 0.08
            notes.append("description too thin (<40 chars)")

    quality = max(0.0, min(1.0, 1.0 - penalty))
    return quality, notes
