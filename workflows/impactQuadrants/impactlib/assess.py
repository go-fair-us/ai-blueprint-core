"""Assess step: one model call per repository places every gap on effort x impact.

The model sees the rubric (rubric.md), the repository's verdicts for context, and its
gap list. It must answer with JSON matching schema/placement-response.schema.json and
exactly one placement per gap id. A fix_label or rationale that only exceeds its
character cap is shortened on a word boundary and kept. Any other invalid answer is
rejected and retried with the validation errors. With --samples N the call is made N
times and the median is used.
Responses are cached under <work>/cache keyed by sha256(prompt + rubric + backend + model
+ sample index), so re-running costs nothing.
"""
from __future__ import annotations

import hashlib
import json
import re
import statistics
import sys
from pathlib import Path

from .backends import BackendError

RESPONSE_SCHEMA = "impact-placements/1"
CONFIDENCE = ("low", "medium", "high")
MAX_LABEL = 40
MAX_RATIONALE = 200

SYSTEM = """You are assessing gaps in a research data repository's support for AI agents.
You do not browse or call tools. You only read the material in the message and answer
with one JSON object, no prose, no Markdown fences."""

OUTPUT_SPEC = """Answer with exactly this JSON shape and nothing else:
{"placements": [
  {"gap_id": "<one of the gap ids above>", "fix_label": "<imperative, <= 40 chars>",
   "x": <effort, number -1..1>, "y": <impact, number -1..1>,
   "rationale": "<one sentence, <= 200 chars>", "confidence": "low" | "medium" | "high"}
]}
Give exactly one placement for every gap id listed, and no others."""


def gap_for_prompt(g: dict) -> dict:
    return {k: g.get(k) for k in ("id", "label", "category", "verdict", "evidence_url",
                                  "summary", "evidence", "report_gaps", "operator_fix")}


def build_prompt(gapfile: dict, rubric_text: str, verdict_context: dict) -> str:
    repo = gapfile["repo"]
    parts = [
        f"# Repository: {repo['name']}",
        f"Origin: {repo.get('url') or 'unknown'}",
        "",
        "## Rubric",
        rubric_text.strip(),
        "",
        "## Verdicts of all checks for this repository (context only)",
        json.dumps(verdict_context, ensure_ascii=False),
        "",
        f"## Gaps to place ({len(gapfile['gaps'])})",
        json.dumps([gap_for_prompt(g) for g in gapfile["gaps"]], indent=1, ensure_ascii=False),
        "",
        "## Output",
        OUTPUT_SPEC,
    ]
    return "\n".join(parts)


def parse_json(text: str):
    """First JSON object in the answer (tolerates ```json fences and surrounding prose)."""
    t = text.strip()
    m = re.search(r"```(?:json)?\s*\n(.*?)```", t, re.S)
    if m:
        t = m.group(1)
    start = t.find("{")
    if start < 0:
        raise ValueError("no JSON object in the answer")
    obj, _ = json.JSONDecoder().raw_decode(t[start:])
    return obj


def validate(obj, gap_ids: list[str]) -> list[str]:
    """Errors (empty list = valid) against the response schema and the gap list."""
    errs = []
    if not isinstance(obj, dict) or not isinstance(obj.get("placements"), list):
        return ["top level must be an object with a 'placements' list"]
    seen = set()
    for i, p in enumerate(obj["placements"]):
        where = f"placements[{i}]"
        if not isinstance(p, dict):
            errs.append(f"{where} is not an object"); continue
        extra = set(p) - {"gap_id", "fix_label", "x", "y", "rationale", "confidence"}
        if extra:
            errs.append(f"{where} has unknown keys {sorted(extra)}")
        gid = p.get("gap_id")
        if gid not in gap_ids:
            errs.append(f"{where}.gap_id {gid!r} is not in the gap list")
        elif gid in seen:
            errs.append(f"{where}.gap_id {gid!r} appears twice")
        seen.add(gid)
        for ax in ("x", "y"):
            v = p.get(ax)
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                errs.append(f"{where}.{ax} must be a number")
            elif not -1 <= v <= 1:
                errs.append(f"{where}.{ax} = {v} is outside -1..1")
        lab = p.get("fix_label")
        if not isinstance(lab, str) or not lab.strip():
            errs.append(f"{where}.fix_label must be a non-empty string")
        elif len(lab) > MAX_LABEL:
            errs.append(f"{where}.fix_label is {len(lab)} chars (max {MAX_LABEL})")
        r = p.get("rationale")
        if not isinstance(r, str) or not r.strip():
            errs.append(f"{where}.rationale must be a non-empty string")
        elif len(r) > MAX_RATIONALE:
            errs.append(f"{where}.rationale is {len(r)} chars (max {MAX_RATIONALE})")
        if p.get("confidence") not in CONFIDENCE:
            errs.append(f"{where}.confidence must be one of {CONFIDENCE}")
    missing = [g for g in gap_ids if g not in seen]
    if missing:
        errs.append(f"missing placements for {missing}")
    return errs


def clip_text(s: str, limit: int) -> str:
    """Shorten s to at most limit characters, ending on a word when one sits near the cut."""
    s = s.strip()
    if len(s) <= limit:
        return s
    cut = s[:limit]
    if s[limit].isspace():
        return cut.rstrip()
    boundary = max(cut.rfind(" "), cut.rfind("\n"), cut.rfind("\t"))
    if boundary >= int(limit * 0.6):
        return cut[:boundary].rstrip()
    return cut


def clip_overlong(obj) -> dict[str, int]:
    """Shorten fix_label and rationale fields that exceed their caps. Other fields stay."""
    counts = {"fix_label": 0, "rationale": 0}
    if not isinstance(obj, dict) or not isinstance(obj.get("placements"), list):
        return counts
    for p in obj["placements"]:
        if not isinstance(p, dict):
            continue
        for field, limit in (("fix_label", MAX_LABEL), ("rationale", MAX_RATIONALE)):
            v = p.get(field)
            if not isinstance(v, str) or len(v) <= limit:
                continue
            clipped = clip_text(v, limit)
            if clipped and clipped != v:
                p[field] = clipped
                counts[field] += 1
    return counts


def _clip_note(counts: dict[str, int]) -> str:
    parts = []
    for field in ("fix_label", "rationale"):
        n = counts.get(field, 0)
        if n:
            parts.append(f"{n} {field}" + ("" if n == 1 else "s"))
    return " and ".join(parts)


def cache_key(prompt: str, rubric, backend, sample: int) -> str:
    h = hashlib.sha256()
    for part in (prompt, rubric.sha, backend.name, str(getattr(backend, "label", "")),
                 str(getattr(backend, "model", "")), str(sample)):
        h.update(part.encode()); h.update(b"\0")
    return h.hexdigest()


def call_validated(backend, prompt: str, gaps: list[dict], max_attempts: int, log) -> tuple[dict, int]:
    ids = [g["id"] for g in gaps]
    user, errors = prompt, []
    for attempt in range(1, max_attempts + 1):
        try:
            text = backend.complete(SYSTEM, user, gaps)
        except BackendError as e:
            raise SystemExit(f"backend {backend.name}: {e}")
        try:
            obj = parse_json(text)
        except (ValueError, json.JSONDecodeError) as e:
            obj, errors = None, [f"answer is not JSON: {e}"]
        else:
            clipped = clip_overlong(obj)
            errors = validate(obj, ids)
            if not errors:
                note = _clip_note(clipped)
                if note:
                    log(f"  attempt {attempt}: clipped {note} to the length cap")
                return {"placements": obj["placements"], "raw": text,
                        "clipped": sum(clipped.values())}, attempt
        log(f"  attempt {attempt}: rejected ({len(errors)} errors: {errors[0]})")
        user = (prompt + "\n\n## Your previous answer was rejected\n" + "\n".join(
            f"- {e}" for e in errors[:20]) + "\nAnswer again with valid JSON only.")
    raise SystemExit(f"no valid answer after {max_attempts} attempts; last errors: {errors[:5]}")


def combine_samples(samples: list[list[dict]], gaps: list[dict], threshold: float) -> list[dict]:
    out = []
    for g in gaps:
        ps = [next(p for p in s if p["gap_id"] == g["id"]) for s in samples]
        xs, ys = [float(p["x"]) for p in ps], [float(p["y"]) for p in ps]
        mx, my = statistics.median(xs), statistics.median(ys)
        rep = min(ps, key=lambda p: (float(p["x"]) - mx) ** 2 + (float(p["y"]) - my) ** 2)
        sx, sy = max(xs) - min(xs), max(ys) - min(ys)
        out.append({"gap_id": g["id"], "fix_label": rep["fix_label"].strip(),
                    "x": round(mx, 3), "y": round(my, 3), "rationale": rep["rationale"].strip(),
                    "confidence": rep["confidence"], "spread_x": round(sx, 3),
                    "spread_y": round(sy, 3),
                    "high_variance": len(ps) > 1 and max(sx, sy) > threshold,
                    "samples": [{"x": float(p["x"]), "y": float(p["y"])} for p in ps]})
    return out


def assess_repo(gapfile: dict, backend, rubric, cfg, work: Path, samples: int,
                verdict_context: dict, log=lambda m: print(m, file=sys.stderr)) -> dict:
    gaps = gapfile["gaps"]
    acfg = cfg["assess"]
    result = {"schema": RESPONSE_SCHEMA, "run": gapfile["run"], "repo": gapfile["repo"],
              "backend": backend.name, "model": backend.label,
              "placeholder": bool(backend.placeholder),
              "rubric_version": rubric.version, "rubric_sha": rubric.sha,
              "samples": samples, "calls": 0, "cache_hits": 0, "attempts": [],
              "clipped": [], "placements": []}
    if not gaps:
        return result
    prompt = build_prompt(gapfile, rubric.text, verdict_context)
    cache = work / "cache"
    cache.mkdir(parents=True, exist_ok=True)
    (work / "prompts").mkdir(exist_ok=True)
    (work / "prompts" / f"{gapfile['repo']['slug']}.txt").write_text(prompt, encoding="utf-8")
    got = []
    for i in range(samples):
        key = cache_key(prompt, rubric, backend, i)
        cp = cache / f"{key}.json"
        if cp.is_file() and not backend.placeholder:
            data = json.loads(cp.read_text())
            if not validate({"placements": data["placements"]}, [g["id"] for g in gaps]):
                got.append(data["placements"]); result["cache_hits"] += 1
                continue
        data, attempts = call_validated(backend, prompt, gaps, int(acfg["max_attempts"]), log)
        result["calls"] += 1
        result["attempts"].append(attempts)
        result["clipped"].append(int(data.get("clipped") or 0))
        if not backend.placeholder:
            cp.write_text(json.dumps({"key": key, **data}, indent=1, ensure_ascii=False))
        got.append(data["placements"])
    result["placements"] = combine_samples(got, gaps, float(acfg["variance_threshold"]))
    return result
