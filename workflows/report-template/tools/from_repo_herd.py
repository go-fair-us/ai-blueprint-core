#!/usr/bin/env python3
"""Turn a repository-herd run folder into the report template's YAML data file.

    python3 tools/from_repo_herd.py RUN_DIR -o data/<stamp>.yaml [--overrides notes.yaml]

RUN_DIR is workflows/repo_herd/runs/<UTC stamp>/ from ai-blueprint-core, as written by
run-repo-herd.sh and `jobs.py finish`. Every value comes from files in that folder:

  manifest.json                    repositories (order, name, origin, question origin), jobs
  summary.md                       per-check verdicts and the property (category) of each check
  <slug>/facet/meta.txt            facet Pi exit code and seconds (minutes on the chart)
  <slug>/facet/command.txt         Pi provider and model
  <slug>/facet/stderr.txt          first line quoted when the facet Pi exit is non-zero
  <slug>/answerability/score.md    competency question ids and grades, in run order
  <slug>/answerability/run-*/      meta.txt (exit codes), report.md (why a row has no answer)
  <slug>/skipped-answerability.md  facet-only repository

Nothing is guessed. A value that is missing from the run is left out and reported as a
warning (on stderr and as comments at the top of the YAML).

Presentation choices that are not data (short check labels, branding text, colours) are
constants below or command-line options, and their defaults match visual-report.pdf.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

# ---------------------------------------------------------------- presentation
# Short column labels for the evaluation ids in jobs.py FACETS (as in visual-report.pdf).
# An evaluation id that is not listed here is shown as-is.
CHECK_LABELS = {
    "reachable-fetch": "reachable", "robots-policy": "robots", "llms-txt": "llms.txt",
    "sitemap": "sitemap", "server-rendered-content": "server HTML",
    "markdown-negotiation": "markdown", "bulk-export": "bulk export",
    "agent-documentation": "agent docs", "openapi-discovery": "OpenAPI",
    "metadata-api": "metadata API", "api-http-behavior": "HTTP API", "mcp-exposure": "MCP",
    "dataset-jsonld": "JSON-LD", "persistent-identifiers": "identifiers",
    "vocabulary": "vocabulary", "metadata-profile": "profile", "shacl-shapes": "SHACL",
    "sssom-mappings": "SSSOM", "competency-questions": "questions",
}
VERDICTS = [  # jobs.py VERDICTS plus "unparsed" for checks the facet report did not include
    {"id": "present", "symbol": "P", "label": "present", "color": "#217A4A", "text": "#FFFFFF"},
    {"id": "partial", "symbol": "~", "label": "partial", "color": "#E3A108", "text": "#261F0D"},
    {"id": "absent", "symbol": "A", "label": "absent", "color": "#C44545", "text": "#FFFFFF"},
    {"id": "blocked", "symbol": "B", "label": "blocked", "color": "#6B4C99", "text": "#FFFFFF"},
    {"id": "not-observable", "symbol": "o", "label": "not-observable", "color": "#D6DBE3", "text": "#404752"},
    {"id": "unparsed", "symbol": "?", "label": "unparsed", "color": "#F5EDD6", "text": "#59471F"},
]
# jobs.py grade_check() / score_run() grades, in legend order. Only grades that occur are shown.
GRADES = {
    "match": {"label": "match", "color": "#217A4A", "text": "#FFFFFF",
              "phrase": "{n} rows matched"},
    "miss": {"label": "miss", "color": "#C44545", "text": "#FFFFFF",
             "phrase": "{n} missed"},
    "ungraded": {"label": "ungraded", "color": "#E3A108", "text": "#261F0D",
                 "phrase": "{n} are ungraded because the check text is outside the three rules"},
    "no-answer": {"label": "no-answer", "color": "#D6DBE3", "text": "#404752",
                  "phrase": "{n} have no answer field"},
    "no-report": {"label": "no-report", "color": "#F5EDD6", "text": "#59471F",
                  "phrase": "{n} have no saved report"},
}
UNPARSED_NOTE = "report did not include this evaluation"  # jobs.py facet_rows() note
FENCE_RE = re.compile(r"```yaml\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)


class Run:
    def __init__(self, run_dir: Path):
        self.dir = run_dir
        self.warnings: list[str] = []

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def read(self, rel: str) -> str | None:
        p = self.dir / rel
        return p.read_text(encoding="utf-8") if p.is_file() else None


# ------------------------------------------------------------------ file parsers
def parse_meta(text: str | None) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in (text or "").splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def parse_model(command: str | None) -> str | None:
    """'--provider nrp --model deepseek-v4-flash' -> 'nrp / deepseek-v4-flash'."""
    if not command:
        return None
    first = command.splitlines()[0]
    prov = re.search(r"--provider[ =](\S+)", first)
    model = re.search(r"--models?[ =](\S+)", first)
    if not model:
        return None
    return f"{prov.group(1)} / {model.group(1)}" if prov else model.group(1)


def split_row(line: str) -> list[str]:
    cells = re.split(r"(?<!\\)\|", line.strip().strip("|"))
    return [c.strip().replace("\\|", "|") for c in cells]


def parse_summary(text: str) -> dict[str, list[dict]]:
    """summary.md -> {repo name: [{property, evaluation, verdict, note}]}."""
    out: dict[str, list[dict]] = {}
    current = None
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            out.setdefault(current, [])
            continue
        if current is None or not re.match(r"^\|\s*\d+\s*\|", line):
            continue
        cells = split_row(line)
        if len(cells) < 4:
            continue
        verdict_cell = cells[3]
        m = re.match(r"^(\S+)\s*(?:\((.*)\))?$", verdict_cell)
        verdict, note = (m.group(1), (m.group(2) or "").strip()) if m else (verdict_cell, "")
        out[current].append({"property": cells[1], "evaluation": cells[2],
                             "verdict": verdict, "note": note})
    return out


def parse_score(text: str) -> list[dict]:
    """score.md -> [{run, id, grade}] in file order (runs, then key-table order)."""
    rows, run = [], None
    header: list[str] = []
    for line in text.splitlines():
        if line.startswith("## "):
            run, header = line[3:].strip(), []
            continue
        if not line.startswith("|"):
            continue
        cells = split_row(line)
        if not header:
            header = cells
            continue
        if all(set(c) <= set("-: ") for c in cells):
            continue
        row = dict(zip(header, cells))
        if row.get("ID"):
            rows.append({"run": run, "id": row["ID"], "grade": row.get("Grade", "")})
    return rows


def answer_problem(report: str | None) -> str | None:
    """Why a run's rows can have no answer: None if the report has a parseable YAML block."""
    if report is None:
        return "no report.md was saved"
    fences = FENCE_RE.findall(report)
    if not fences:
        return "its report has no fenced YAML block"
    for chunk in fences:
        try:
            data = yaml.safe_load(chunk)
        except yaml.YAMLError:
            continue
        if isinstance(data, dict) and ("checks" in data or "evaluation" in data):
            return None
    return "its YAML block did not parse"


def display_name(name: str, full: bool) -> str:
    """'AccessClinicalData@NIAID (ACDN)' -> 'ACDN' unless --full-names."""
    m = re.match(r"^.*\(([^()]+)\)\s*$", name)
    return name if full or not m else m.group(1).strip()


def stamp_date(stamp: str) -> str | None:
    try:
        dt = datetime.strptime(stamp, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return None
    return f"{dt.day} {dt.strftime('%B %Y, %H:%M')} UTC"


def join_and(items: list[str]) -> str:
    items = list(items)
    if len(items) <= 1:
        return "".join(items)
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + ", and " + items[-1]


def deep_merge(base: dict, extra: dict) -> dict:
    for k, v in extra.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            deep_merge(base[k], v)
        else:
            base[k] = v
    return base


# ---------------------------------------------------------------------- convert
def convert(run_dir: Path, *, full_names: bool = False, rename: dict | None = None, org: str = "NIAID Blueprint repository herd",
            site_label: str = "NIAID repository sites", check_label: str = "webinar checks",
            title: str = "Repository agent-access review") -> tuple[dict, list[str]]:
    run = Run(Path(run_dir))
    stamp = run.dir.name
    manifest_text = run.read("manifest.json")
    if manifest_text is None:
        raise SystemExit(f"{run.dir}: no manifest.json; is this a repo_herd run folder?")
    manifest = json.loads(manifest_text)
    repos = manifest.get("repos") or []
    jobs = manifest.get("jobs") or []
    if not repos:
        raise SystemExit(f"{run.dir}/manifest.json lists no repositories")

    # ---- verdicts per repo -------------------------------------------------
    summary_text = run.read("summary.md")
    if summary_text is None:
        run.warn("summary.md is missing (run `jobs.py finish --out RUN_DIR`); no check verdicts")
        summary = {}
    else:
        summary = parse_summary(summary_text)

    checks: list[dict] = []
    seen_checks: dict[str, dict] = {}
    categories: list[dict] = []
    seen_cats: set[str] = set()
    known = {v["id"] for v in VERDICTS}

    out_repos = []
    names_used: set[str] = set()
    for repo in repos:
        slug, name = repo.get("slug"), repo.get("name", "")
        shown = (rename or {}).get(name) or display_name(name, full_names)
        if shown in names_used:      # two repos with the same abbreviation: keep full names
            shown = name
        names_used.add(shown)
        entry: dict = {"name": shown}
        origin = repo.get("origin")
        if origin:
            entry["url"] = origin
        else:
            run.warn(f"{name}: manifest has no origin URL")

        facet_dir = run.dir / slug / "facet"
        meta = parse_meta(run.read(f"{slug}/facet/meta.txt")) if facet_dir.is_dir() else {}
        if facet_dir.is_dir():
            if "seconds" in meta and meta["seconds"].isdigit():
                entry["minutes"] = round(int(meta["seconds"]) / 60)
            else:
                run.warn(f"{name}: facet/meta.txt has no seconds; minutes left out")
            if meta.get("exit_code") not in (None, "0"):
                entry["_facet_exit"] = meta.get("exit_code")
                err = (run.read(f"{slug}/facet/stderr.txt") or "").strip().splitlines()
                entry["_facet_stderr"] = err[0].strip() if err else ""
            elif "exit_code" not in meta:
                run.warn(f"{name}: facet/meta.txt missing or has no exit_code")

        rows = summary.get(name)
        verdicts: dict[str, str] = {}
        if rows is None:
            if summary:
                run.warn(f"{name}: no section in summary.md; no check verdicts")
        elif not rows:
            run.warn(f"{name}: summary.md has no check table (facet job not run or no report)")
        for row in rows or []:
            cat_label = re.sub(r"^Be\s+", "", row["property"]).strip() or row["property"]
            cat_id = re.sub(r"[^a-z0-9]+", "-", cat_label.lower()).strip("-")
            if cat_id not in seen_cats:
                seen_cats.add(cat_id)
                categories.append({"id": cat_id, "label": cat_label})
            ev = row["evaluation"]
            if ev not in seen_checks:
                seen_checks[ev] = {"id": ev, "label": CHECK_LABELS.get(ev, ev), "category": cat_id}
                checks.append(seen_checks[ev])
            elif seen_checks[ev]["category"] != cat_id:
                run.warn(f"{name}/{ev}: property {row['property']!r} differs from another repository")
            v = row["verdict"]
            if v == "not-observable" and row["note"] == UNPARSED_NOTE:
                v = "unparsed"
            if v not in known:
                run.warn(f"{name}/{ev}: verdict {row['verdict']!r} is not in the vocabulary; left out")
                continue
            verdicts[ev] = v
        entry["verdicts"] = verdicts

        # ---- competency questions -------------------------------------
        ans_dir = run.dir / slug / "answerability"
        skipped = (run.dir / slug / "skipped-answerability.md").is_file()
        entry["_skipped"] = skipped
        entry["_question_origin"] = repo.get("question_origin")
        problems: dict[str, str] = {}
        if ans_dir.is_dir():
            score = run.read(f"{slug}/answerability/score.md")
            if score is None:
                run.warn(f"{name}: answerability/score.md missing (run `jobs.py finish`); questions left out")
            else:
                qs = parse_score(score)
                for q in qs:
                    if q["grade"] not in GRADES:
                        run.warn(f"{name}/{q['id']}: grade {q['grade']!r} unknown; shown with a grey tile")
                entry["questions"] = [{"id": q["id"], "grade": q["grade"]} for q in qs]
                for rd in sorted(p for p in ans_dir.iterdir() if p.is_dir()):
                    pr = answer_problem(run.read(f"{slug}/answerability/{rd.name}/report.md"))
                    if pr:
                        problems[rd.name] = pr
                entry["_q_runs"] = {q["id"]: q["run"] for q in qs}
        elif not skipped and facet_dir.is_dir():
            run.warn(f"{name}: neither answerability/ nor skipped-answerability.md")
        entry["_problems"] = problems
        out_repos.append(entry)

    # ---- Pi jobs --------------------------------------------------------
    exits = []
    for job in jobs:
        m = parse_meta(run.read(f"{job.get('dir', '')}/meta.txt"))
        if "exit_code" not in m:
            run.warn(f"job {job.get('id')}: no meta.txt exit code (job never finished?)")
        exits.append(m.get("exit_code"))
    n_ok = sum(1 for e in exits if e == "0")

    model = None
    for job in jobs:
        model = parse_model(run.read(f"{job.get('dir', '')}/command.txt"))
        if model:
            break
    if not model:
        run.warn("no Pi --model found in any command.txt; footer omits the model")

    # ---- text --------------------------------------------------------------
    date = stamp_date(stamp)
    if not date:
        run.warn(f"folder name {stamp!r} is not a UTC stamp; subtitle has no date")
    subtitle = " · ".join(x for x in [
        "{{ n_repos|words|capitalize }} " + site_label,
        "{{ n_checks }} " + check_label, date] if x)
    footer = " · ".join(x for x in [org, f"stamp {stamp}", model] if x)

    failed = [r for r in out_repos if r.get("_facet_exit")]
    mix_note = ("P present, ~ partial, A absent, B blocked, o not-observable, ? the report had no "
                "parseable YAML block for that check. A ? is a summarizer gap, not an agent verdict.")
    if failed:
        bits = []
        for r in failed:
            s = f"{r['name']} facet exited {r['_facet_exit']}"
            if r["_facet_stderr"]:
                s += f" (stderr: {r['_facet_stderr'].rstrip('.')})"
            bits.append(s)
        mix_note += " " + join_and(bits) + "."

    cat_counts = {c["id"]: sum(1 for k in checks if k["category"] == c["id"]) for c in categories}
    grid_notes = []
    if categories:
        grid_notes.append(
            "Columns follow summary.md: " + join_and(
                [f"{c['label']} ({cat_counts[c['id']]} {'check' if cat_counts[c['id']] == 1 else 'checks'})"
                 for c in categories]) + ".")
    blocked = [(r["name"], sum(1 for v in r["verdicts"].values() if v == "blocked")) for r in out_repos]
    blocked = [f"{n} {c}" for n, c in blocked if c]
    if blocked:
        grid_notes.append("Blocked checks: " + join_and(blocked) + ".")

    grades_present = [g for g in GRADES if any(q["grade"] == g for r in out_repos for q in r.get("questions", []))]
    extra_grades = sorted({q["grade"] for r in out_repos for q in r.get("questions", [])} - set(GRADES))
    phrases = [GRADES[g]["phrase"].format(
        n="{{ q['%s']|words%s }}" % (g, "|capitalize" if i == 0 else "")) for i, g in enumerate(grades_present)]
    comp_caption = "The grader scores checks[].answer only. " + join_and(phrases) + "." if phrases else \
        "The grader scores checks[].answer only."

    notes = []
    by_reason: dict[str, list[str]] = {}
    for r in out_repos:
        for run_name, why in r["_problems"].items():
            grades = {q["id"]: q["grade"] for q in r.get("questions", [])}
            ids = [qid for qid, rn in r.get("_q_runs", {}).items()
                   if rn == run_name and grades.get(qid) in ("no-answer", "no-report")]
            if ids:
                by_reason.setdefault(why, []).extend(ids)
    if by_reason:
        parts = [f"{why.replace('its report', 'the report').replace('its YAML', 'the YAML')} "
                 f"({', '.join(items)})" for why, items in by_reason.items()]
        notes.append("Scored no-answer because " + " or ".join(parts) + ".")
    explained = {qid for r in out_repos for rn in r["_problems"]
                 for qid, x in r.get("_q_runs", {}).items() if x == rn}
    empty = [q["id"] for r in out_repos for q in r.get("questions", [])
             if q["grade"] == "no-answer" and q["id"] not in explained]
    if empty:
        notes.append(f"Empty answer field, scored no-answer: {join_and(empty)}.")
    ung = [q["id"] for r in out_repos for q in r.get("questions", []) if q["grade"] == "ungraded"]
    if ung:
        notes.append(f"Ungraded (Check cell outside the three rules, see score.md): {join_and(ung)}.")
    for r in out_repos:
        qo = r["_question_origin"]
        if r.get("questions") and qo and r.get("url") and qo != r["url"]:
            notes.append(f"{r['name']} questions ran against {qo}; the facet review used {r['url']}.")
    if any(r["_skipped"] for r in out_repos):
        notes.append("{{ no_question_repos|join_and }} have a facet review only. "
                     "This herd does not invent competency questions for them.")

    data = {
        "report": {"title": title, "subtitle": subtitle, "footer": footer,
                   "pdf_title": f"{title}, {stamp}", "author": org},
        "summary_cards": [
            {"value": "{{ n_repos }}", "label": "repositories reviewed"},
            *([{"value": f"{n_ok} of {len(jobs)}", "label": "Pi jobs exited 0"}] if jobs else []),
            {"value": "{{ totals.present }}", "label": "checks scored present"},
        ],
        "verdicts": VERDICTS,
        "categories": categories or [{"id": "none", "label": "none"}],
        "checks": checks,
        "question_grades": [{"id": g, **{k: GRADES[g][k] for k in ("label", "color", "text")}}
                            for g in grades_present]
                           + [{"id": g, "label": g, "color": "#D6DBE3", "text": "#404752"} for g in extra_grades],
        "sections": {
            "verdict_mix": {
                "heading": "Verdict mix",
                "caption": "{% if uniform_checks %}Each bar is the {{ n_checks }} checks for that repository."
                           "{% else %}Bar length is the number of checks reported for that repository."
                           "{% endif %} Minutes are the facet Pi run.",
                "footnote": mix_note,
            },
            "check_grid": {
                "heading": "Check by repository",
                "caption": "{% if uniform_checks %}Same {{ n_checks }} checks, left to right.{% else %}"
                           "{{ n_checks }} checks, left to right.{% endif %} Color is the summary verdict. "
                           "The letter repeats the color for a black-and-white copy.",
                "footnote": grid_notes,
            },
            "competency": {
                "heading": "Competency questions",
                "caption": comp_caption,
                "notes_heading": "How to read the grades",
                "notes": notes,
            },
        },
        "repositories": [],
    }
    check_ids = [c["id"] for c in checks]
    for r in out_repos:
        e = {k: v for k, v in r.items() if not k.startswith("_")}
        sym = {v["id"]: v["symbol"] for v in VERDICTS}
        if list(e["verdicts"]) == check_ids:
            e["verdicts"] = " ".join(sym[e["verdicts"][c]] for c in check_ids)
        else:
            if check_ids and r["verdicts"]:
                missing = [c for c in check_ids if c not in r["verdicts"]]
                if missing:
                    run.warn(f"{r['name']}: {len(missing)} check(s) not in summary.md: {', '.join(missing)}")
            e["verdicts"] = {c: sym[v] for c, v in e["verdicts"].items()}
        data["repositories"].append(e)
    if not checks:
        run.warn("no checks found at all; the grid and bars will be empty")
    return data, run.warnings


def dump(data: dict, warnings: list[str], run_dir: Path) -> str:
    head = [f"# Generated by tools/from_repo_herd.py from {run_dir}",
            "# Edit the run (or pass --overrides) rather than this file; it is rebuilt each time."]
    if warnings:
        head.append("# Warnings (values left out rather than guessed):")
        head += [f"#   - {w}" for w in warnings]
    body = yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=120)
    return "\n".join(head) + "\n" + body


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="repo_herd run folder -> report data YAML")
    ap.add_argument("run_dir", type=Path)
    ap.add_argument("-o", "--out", type=Path, help="output YAML (default data/<stamp>.yaml)")
    ap.add_argument("--overrides", type=Path, help="YAML merged on top (e.g. hand-written notes)")
    ap.add_argument("--full-names", action="store_true",
                    help="use full CSV names instead of the abbreviation in parentheses")
    ap.add_argument("--rename", action="append", default=[], metavar="CSV_NAME=SHOWN",
                    help="display name for one repository, e.g. --rename VeuPathDB=VEuPathDB (repeatable)")
    ap.add_argument("--org", default="NIAID Blueprint repository herd", help="footer/author text")
    ap.add_argument("--site-label", default="NIAID repository sites")
    ap.add_argument("--check-label", default="webinar checks")
    ap.add_argument("--title", default="Repository agent-access review")
    a = ap.parse_args(argv)
    rename = dict(x.split("=", 1) for x in a.rename if "=" in x)
    data, warnings = convert(a.run_dir, full_names=a.full_names, rename=rename, org=a.org,
                             site_label=a.site_label, check_label=a.check_label, title=a.title)
    if a.overrides:
        deep_merge(data, yaml.safe_load(a.overrides.read_text()) or {})
    out = a.out or Path(__file__).resolve().parents[1] / "data" / f"{a.run_dir.resolve().name}.yaml"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(dump(data, warnings, a.run_dir))
    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
