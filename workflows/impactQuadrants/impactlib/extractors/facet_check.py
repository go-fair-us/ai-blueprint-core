"""Gap source "facet-check": the 19 webinar checks of a repo_herd facet job.

A gap is a check whose summary.md verdict is in cfg["gap_verdicts"]["facet-check"]
(default: absent only). Every other verdict is counted in non_gaps and not plotted.
Evidence comes from the check's fenced YAML block in facet/report.md; the operator-fix
text is the prose of the report section for the check's property ("Be readable" ...).
"""
from __future__ import annotations

import re
from collections import Counter

from ..runfiles import category_label, check_label, load_yaml_blocks, raw_block
from . import ExtractResult, register

SOURCE = "facet-check"
HEADING_RE = re.compile(r"^(#{1,4})\s+(.*)$")
MAX_EVIDENCE = 8
MAX_LINE = 320
MAX_FIX = 1600


def _strip_code(text: str) -> str:
    return re.sub(r"```.*?```", "", text, flags=re.S)


def _paragraphs(text: str) -> list[str]:
    paras, cur = [], []
    for line in _strip_code(text).splitlines():
        s = line.strip()
        if not s or s.startswith(("|", "---", "#")) or re.match(r"^\*Script JSON", s):
            if cur:
                paras.append(" ".join(cur)); cur = []
            continue
        cur.append(s)
    if cur:
        paras.append(" ".join(cur))
    return [p for p in paras if len(p) > 40]


def sections(text: str) -> list[tuple[str, str]]:
    """[(heading text, body)] at any heading level 1-4."""
    out, head, body = [], None, []
    for line in (text or "").splitlines():
        m = HEADING_RE.match(line)
        if m and not line.startswith("#####"):
            if head is not None:
                out.append((head, "\n".join(body)))
            head, body = m.group(2).strip(), []
        else:
            body.append(line)
    if head is not None:
        out.append((head, "\n".join(body)))
    return out


def operator_fix(report: str | None, prop: str) -> str:
    """Prose that says what an operator should do for this property."""
    if not report:
        return ""
    cat = re.escape(category_label(prop).lower())
    found: list[str] = []
    for head, body in sections(report):
        if re.search(rf"\bbe\s+{cat}\b", head, re.I):
            found += _paragraphs(body)
    if not found:   # "## What the operator should do next" with "**Be readable.** ..." paragraphs
        for p in _paragraphs(report):
            if re.match(rf"^\*\*be\s+{cat}\b", p, re.I):
                found.append(p)
    text = " ".join(found).replace("**", "")
    return text[:MAX_FIX].rstrip() + ("…" if len(text) > MAX_FIX else "")


def _short(s) -> str:
    s = re.sub(r"\s+", " ", str(s)).strip()
    return s[:MAX_LINE] + ("…" if len(s) > MAX_LINE else "")


def evidence_from_doc(doc: dict) -> tuple[list[str], str, list[str]]:
    """(evidence lines for non-passing sub-checks, summary, report gaps)."""
    lines = []
    for c in doc.get("checks") or []:
        if not isinstance(c, dict):
            continue
        if str(c.get("result", "")).lower() == "pass":
            continue
        lines.append(_short(f"{c.get('id', '?')}: {c.get('result', '?')} — {c.get('evidence', '')}"))
    gaps = [_short(g) for g in (doc.get("gaps") or []) if g]
    return lines[:MAX_EVIDENCE], _short(doc.get("summary") or ""), gaps[:5]


@register(SOURCE)
def extract(run, repo, cfg) -> ExtractResult:
    gap_verdicts = set((cfg.get("gap_verdicts") or {}).get(SOURCE, ["absent"]))
    if not repo.rows:
        return ExtractResult(available=False,
                             notes=["no facet check results in summary.md for this repository"])
    docs, broken = load_yaml_blocks(repo.facet_report or "")
    res = ExtractResult()
    counts = Counter()
    for row in repo.rows:
        v, ev = row["verdict"], row["evaluation"]
        if v not in gap_verdicts:
            counts[v] += 1
            continue
        doc = docs.get(ev)
        if doc is not None:
            evidence, summary, rgaps = evidence_from_doc(doc)
            parsed = True
        else:
            raw = raw_block(repo.facet_report or "", ev)
            evidence = [_short(l) for l in (raw or "").splitlines() if "evidence" in l][:MAX_EVIDENCE]
            summary, rgaps, parsed = "", [], False
            res.notes.append(f"{ev}: YAML block did not parse; evidence taken from raw lines"
                             if raw else f"{ev}: no YAML block found; verdict from summary.md only")
        res.gaps.append({
            "id": f"{SOURCE}:{ev}",
            "source": SOURCE,
            "key": ev,
            "label": check_label(ev),
            "category": category_label(row["property"]),
            "verdict": v,
            "evidence_url": row.get("evidence_url") or "",
            "evidence": evidence,
            "summary": summary,
            "report_gaps": rgaps,
            "operator_fix": operator_fix(repo.facet_report, row["property"]),
            "context": {"property": row["property"], "position": row["n"], "block_parsed": parsed},
        })
    res.non_gaps = dict(counts)
    res.context = {"verdicts": {r["evaluation"]: r["verdict"] for r in repo.rows}}
    if broken:
        res.notes.append("YAML blocks that did not parse: " + ", ".join(sorted(set(broken))))
    return res
