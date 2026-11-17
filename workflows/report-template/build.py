#!/usr/bin/env python3
"""Build the agent-access review PDF from a YAML/JSON data file.

    python3 build.py data/example.yaml -o out/example.pdf [--html out/example.html]
    python3 build.py --run path/to/workflows/repo_herd/runs/<stamp> -o out/<stamp>.pdf

Everything that can vary (repositories, checks per repository, categories,
competency questions, summary cards) comes from the data file. Layout and
pagination adapt to the counts.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import OrderedDict
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from theme import theme  # noqa: E402

# ---------------------------------------------------------------- layout knobs
LAYOUT = {
    "content_w": 728.0,        # 792 - 2 * 32 pt margins
    "mix_rows_first": 13,      # verdict-mix bars on page 1 (under the cards)
    "mix_rows_next": 17,       # bars on each continuation page
    "grid_rows": 13,           # repository rows per check-grid page
    "grid_avail": 646.0,       # width for check columns (19 x 34 pt, as in the original)
    "grid_pitch_max": 34.0,    # column pitch in the original
    "grid_pitch_min": 21.0,    # below this, columns split onto another page
    "tiles_per_row": 7,        # competency tiles per row (92 pt + 6 pt gap)
}

NUM_WORDS = ("zero one two three four five six seven eight nine ten eleven twelve "
             "thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty").split()


def words(n):
    """12 -> 'twelve' (0-20), larger numbers stay as digits."""
    try:
        n = int(n)
    except (TypeError, ValueError):
        return n
    return NUM_WORDS[n] if 0 <= n <= 20 else str(n)


def join_and(items):
    items = [str(i) for i in items]
    if len(items) <= 1:
        return "".join(items)
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + ", and " + items[-1]


def plural(n, one, many=None):
    return one if int(n) == 1 else (many or one + "s")


class DataError(ValueError):
    pass


# --------------------------------------------------------------------- loading
def load(path: Path) -> dict:
    text = path.read_text()
    data = json.loads(text) if path.suffix == ".json" else yaml.safe_load(text)
    if not isinstance(data, dict):
        raise DataError("top level must be a mapping")
    return data


def schema_check(data: dict) -> None:
    """Validate against schema/report.schema.json when `jsonschema` is installed.
    build.py also runs its own checks below, so this is optional."""
    try:
        import jsonschema
    except ImportError:
        return
    schema = json.loads((ROOT / "schema" / "report.schema.json").read_text())
    errors = sorted(jsonschema.Draft202012Validator(schema).iter_errors(data), key=str)
    if errors:
        raise DataError("\n".join(f"{'/'.join(map(str, e.path)) or '(top)'}: {e.message}"
                                   for e in errors[:20]))


def normalise(data: dict) -> dict:
    """Validate the data and compute every derived count."""
    schema_check(data)
    errs = []
    for key in ("report", "verdicts", "categories", "checks", "repositories"):
        if key not in data:
            errs.append(f"missing top-level key: {key}")
    if errs:
        raise DataError("\n".join(errs))

    verdicts = data["verdicts"]
    by_vid = {v["id"]: v for v in verdicts}
    by_sym = {str(v["symbol"]): v for v in verdicts}

    cats = []
    for i, c in enumerate(data["categories"]):
        c = dict(c)
        c.setdefault("label", c["id"])
        c.setdefault("tint", theme.CATEGORY_TINTS[i % len(theme.CATEGORY_TINTS)])
        cats.append(c)
    cat_ids = [c["id"] for c in cats]

    checks = []
    seen = set()
    for c in data["checks"]:
        if c["id"] in seen:
            errs.append(f"duplicate check id {c['id']}")
        seen.add(c["id"])
        if c.get("category") not in cat_ids:
            errs.append(f"check {c['id']}: unknown category {c.get('category')!r}")
        checks.append({"label": c["id"], **c})
    # column order: category order, then file order within a category
    checks.sort(key=lambda c: cat_ids.index(c["category"]) if c["category"] in cat_ids else 99)
    check_ids = [c["id"] for c in data["checks"]]  # order used by string-form verdicts
    check_by_id = {c["id"]: c for c in checks}

    grades = data.get("question_grades", [])
    grade_ids = [g["id"] for g in grades]

    repos = []
    for r in data["repositories"]:
        r = dict(r)
        name = r.get("name") or "?"
        raw = r.get("verdicts", {})
        if isinstance(raw, str):
            syms = raw.split()
            if len(syms) != len(check_ids):
                errs.append(f"{name}: verdict string has {len(syms)} symbols, "
                            f"but there are {len(check_ids)} checks")
            raw = dict(zip(check_ids, syms))
        res = {}
        for cid, v in (raw or {}).items():
            if cid not in check_by_id:
                errs.append(f"{name}: unknown check {cid!r}")
                continue
            vv = by_vid.get(str(v)) or by_sym.get(str(v))
            if vv is None:
                errs.append(f"{name}/{cid}: unknown verdict {v!r}")
                continue
            res[cid] = vv["id"]
        r["results"] = res
        r["counts"] = OrderedDict((v["id"], 0) for v in verdicts)
        for vid in res.values():
            r["counts"][vid] += 1
        r["total"] = len(res)
        r["category_counts"] = OrderedDict(
            (c, sum(1 for cid in res if check_by_id[cid]["category"] == c)) for c in cat_ids)
        r["n_categories"] = sum(1 for n in r["category_counts"].values() if n)
        qs = r.get("questions") or []
        for q in qs:
            if grades and q.get("grade") not in grade_ids:
                errs.append(f"{name}/{q.get('id')}: unknown grade {q.get('grade')!r}")
        r["questions"] = qs
        repos.append(r)
    if errs:
        raise DataError("\n".join(errs))

    # Only show checks/categories that at least one repository used.
    used = {cid for r in repos for cid in r["results"]}
    checks = [c for c in checks if c["id"] in used] or checks
    cats_used = [c for c in cats if any(k["category"] == c["id"] for k in checks)]

    totals = OrderedDict((v["id"], sum(r["counts"][v["id"]] for r in repos)) for v in verdicts)
    q = OrderedDict((g, sum(1 for r in repos for x in r["questions"] if x.get("grade") == g))
                    for g in grade_ids)
    uniform = all(r["total"] == len(checks) for r in repos)

    ctx = {
        "data": data,
        "report": data["report"],
        "verdicts": verdicts,
        "categories": cats_used,
        "checks": checks,
        "repositories": repos,
        "question_grades": grades,
        "n_repos": len(repos),
        "n_checks": len(checks),
        "n_categories": len(cats_used),
        "checks_min": min((r["total"] for r in repos), default=0),
        "checks_max": max((r["total"] for r in repos), default=0),
        "checks_total": sum(r["total"] for r in repos),
        "uniform_checks": uniform,
        "totals": totals,
        "q": q,
        "n_questions": sum(q.values()) if q else sum(len(r["questions"]) for r in repos),
        "question_repos": [r["name"] for r in repos if r["questions"]],
        "no_question_repos": [r["name"] for r in repos if not r["questions"]],
        "layout": LAYOUT,
    }
    return ctx


# ------------------------------------------------------------------- rendering
def make_env() -> Environment:
    env = Environment(loader=FileSystemLoader(ROOT / "templates"),
                      autoescape=select_autoescape(["html", "j2"]),
                      undefined=StrictUndefined, trim_blocks=True, lstrip_blocks=True)
    env.filters.update(words=words, join_and=join_and, plural=plural,
                       sep=lambda t: str(t).replace(' · ', '  ·  '))
    return env


def render_text(env, value, ctx):
    """Render Jinja inside data-file text fields (strings, lists, dicts)."""
    if isinstance(value, str):
        return env.from_string(value).render(**ctx) if "{" in value else value
    if isinstance(value, list):
        return [render_text(env, v, ctx) for v in value]
    if isinstance(value, dict):
        return {k: render_text(env, v, ctx) for k, v in value.items()}
    return value


def chunks(seq, first, rest):
    out, i = [], 0
    size = first
    while i < len(seq) or not out:
        out.append(seq[i:i + size])
        i += size
        size = rest
    return out


def footnote_lines(note, size, lead):
    """Estimated wrapped line count of a footnote (string or list) at the content width."""
    if not note:
        return 0
    paras = [note] if isinstance(note, str) else note
    return sum(max(1, math.ceil(theme.text_width(str(p), size) / LAYOUT["content_w"])) for p in paras)


def fit_last(parts, cap_last):
    """Make sure the last chunk leaves room for its footnote; spill to a new page."""
    cap_last = max(1, cap_last)
    if parts and len(parts[-1]) > cap_last:
        last = parts.pop()
        parts += [last[:cap_last], last[cap_last:]]
    return parts


def column_blocks(checks, cats, name_w=82.0):
    """Split check columns into page-width blocks, never below the min pitch."""
    max_cols = int((LAYOUT["grid_avail"] - (name_w - 82.0)) // LAYOUT["grid_pitch_min"])
    if len(checks) <= max_cols:
        return [checks]
    blocks, cur = [], []
    for cat in cats:
        group = [c for c in checks if c["category"] == cat["id"]]
        while group:
            room = max_cols - len(cur)
            if len(group) > room and cur:      # start a new block at a category edge
                blocks.append(cur)
                cur = []
                continue
            take = group[:max_cols - len(cur)]
            cur += take
            group = group[len(take):]
            if len(cur) == max_cols:
                blocks.append(cur)
                cur = []
    if cur:
        blocks.append(cur)
    return blocks


def grid_label_width(repos):
    """Row-label column: 82 pt as in the original, wider for long names (max 160)."""
    longest = max((theme.text_width(r["name"], 8) for r in repos), default=0)
    return min(160.0, max(82.0, math.ceil(longest + 8)))


def grid_geometry(cols, cats, name_w=82.0):
    avail = LAYOUT["grid_avail"] - (name_w - 82.0)
    pitch = min(LAYOUT["grid_pitch_max"], avail / max(len(cols), 1))
    bands = []
    for cat in cats:
        n = sum(1 for c in cols if c["category"] == cat["id"])
        if n:
            bands.append({**cat, "n": n, "width": n * pitch - 2})
    return {"pitch": pitch, "cell_w": pitch - 3 if pitch < 34 else 31.0, "bands": bands,
            "name_w": name_w, "x0": name_w + 5.5}


def build(data_path: Path, pdf_path: Path, html_path: Path | None = None) -> Path:
    data = load(data_path)
    ctx = normalise(data)
    env = make_env()
    ctx["report"] = render_text(env, data["report"], ctx)
    ctx["summary_cards"] = render_text(env, data.get("summary_cards", []), ctx)
    ctx["sections"] = render_text(env, data.get("sections", {}), ctx)

    repos = ctx["repositories"]
    uniform = ctx["uniform_checks"]

    # Verdict-mix chart pages
    rows = []
    for r in repos:
        right = []
        if not uniform:
            right.append(f"{r['total']} {plural(r['total'], 'check')}")
        if r.get("minutes") is not None:
            right.append(f"{r['minutes']} min")
        rows.append({"name": r["name"], "counts": r["counts"], "total": r["total"],
                     "right": " · ".join(right)})
    n_cards = len(ctx["summary_cards"])
    ctx["cards_per_row"] = per_row = 3 if n_cards <= 3 else min(n_cards, 5)
    ctx["card_w"] = 230.0 if per_row == 3 else (LAYOUT["content_w"] - 14 * (per_row - 1)) / per_row
    card_rows = math.ceil(n_cards / per_row) if n_cards else 0
    first = LAYOUT["mix_rows_first"] - (card_rows - 1) * 3 + (3 if card_rows == 0 else 0)
    mix_note_rows = math.ceil(max(0, footnote_lines(ctx["sections"].get("verdict_mix", {}).get("footnote"), 8, 11) - 2) * 11 / 24)
    # same label column and scale on every continuation page
    label_w = max([108.0] + [theme.text_width(r["name"], 8.5) + 2 for r in rows])
    max_total = max((r["total"] for r in rows), default=1) or 1
    parts = chunks(rows, first, LAYOUT["mix_rows_next"])
    parts = fit_last(parts, (first if len(parts) == 1 else LAYOUT["mix_rows_next"]) - mix_note_rows)
    ctx["mix_pages"] = [
        {"svg": theme.stacked_hbar(part, ctx["verdicts"], uniform=uniform, label_w=label_w,
                                   max_total=max_total), "rows": len(part)}
        for part in parts
    ]

    # Check-grid pages: column blocks x row chunks
    grid_pages = []
    name_w = grid_label_width(repos)
    blocks = column_blocks(ctx["checks"], ctx["categories"], name_w)
    grid_note_rows = math.ceil(max(0, footnote_lines(ctx["sections"].get("check_grid", {}).get("footnote"), 8, 12) - 2) * 12 / 26)
    for bi, cols in enumerate(blocks):
        geo = grid_geometry(cols, ctx["categories"], name_w)
        parts = chunks(repos, LAYOUT["grid_rows"], LAYOUT["grid_rows"])
        if bi == len(blocks) - 1:  # the footnote sits on the very last grid page
            parts = fit_last(parts, LAYOUT["grid_rows"] - grid_note_rows)
        for part in parts:
            grid_pages.append({"cols": cols, "rows": part, **geo,
                               "block": bi + 1, "n_blocks": len(blocks)})
    for i, gp in enumerate(grid_pages):
        gp["first"] = i == 0
        gp["last"] = i == len(grid_pages) - 1
    ctx["grid_pages"] = grid_pages

    ctx["by_verdict"] = {v["id"]: v for v in ctx["verdicts"]}
    ctx["by_grade"] = {g["id"]: g for g in ctx["question_grades"]}
    ctx["css"] = (ROOT / "templates" / "report.css").read_text()

    html = env.get_template("report.html.j2").render(**ctx)
    if html_path:
        html_path.parent.mkdir(parents=True, exist_ok=True)
        html_path.write_text(html)

    from weasyprint import HTML  # imported late: slow import
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html, base_url=str(ROOT)).write_pdf(str(pdf_path))
    return pdf_path


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("data", type=Path, nargs="?", help="YAML or JSON data file")
    ap.add_argument("--run", type=Path, metavar="RUN_DIR",
                    help="build straight from a repo_herd run folder (writes data/<stamp>.yaml first)")
    ap.add_argument("--overrides", type=Path, help="with --run: YAML merged over the generated data")
    ap.add_argument("--rename", action="append", default=[], metavar="CSV_NAME=SHOWN",
                    help="with --run: display name for one repository (repeatable)")
    ap.add_argument("--data-out", type=Path, help="with --run: where to write the generated YAML")
    ap.add_argument("-o", "--out", type=Path, help="output PDF (default out/<data>.pdf)")
    ap.add_argument("--html", type=Path, help="also write the intermediate HTML here")
    a = ap.parse_args(argv)
    if a.run:
        from tools import from_repo_herd as frh
        stamp = a.run.resolve().name
        a.data = a.data_out or ROOT / "data" / f"{stamp}.yaml"
        conv = [str(a.run), "-o", str(a.data)]
        if a.overrides:
            conv += ["--overrides", str(a.overrides)]
        for r in a.rename:
            conv += ["--rename", r]
        frh.main(conv)
    elif a.data is None:
        ap.error("give a data file or --run RUN_DIR")
    out = a.out or ROOT / "out" / (a.data.stem + ".pdf")
    try:
        build(a.data, out, a.html)
    except DataError as e:
        sys.exit(f"data error in {a.data}:\n{e}")
    print(out)


if __name__ == "__main__":
    main()
