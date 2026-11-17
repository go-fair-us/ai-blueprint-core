"""Report step: placements -> one PDF (WeasyPrint), in the agent-access report style."""
from __future__ import annotations

import io
import json
import math
import sys
from collections import Counter
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

from . import style
from .combine import combine
from .review import load_overrides, load_placements
from .rubric import load as load_rubric
from .runfiles import VERDICTS

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import quadrant_plot as qp  # noqa: E402

NUM_WORDS = ("zero one two three four five six seven eight nine ten eleven twelve "
             "thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty").split()
WATERMARK = "PLACEHOLDER \u00b7 not model output"

LAYOUT = {
    "combined_w": 452, "combined_h": 368,
    "repo_w": 372, "repo_h": 392,
    "ranked_first": 22, "ranked_next": 34,
    "sheet_h": 543.5, "head_h": 64, "head_h_next": 34, "banner_h": 42, "banner_small_h": 22, "th_h": 16,
    "foot_line": 10, "max_labels": 14, "max_labels_combined": 26, "label_budget": 1900,
    "rationale_w": 188, "rationale_w_full": 500,
}


def words(n: int, cap: bool = False) -> str:
    s = NUM_WORDS[n] if 0 <= n <= 20 else str(n)
    return s[:1].upper() + s[1:] if cap else s


def plural(n, one, many=None):
    return one if n == 1 else (many or one + "s")


def join_and(items):
    items = [str(i) for i in items]
    if len(items) <= 1:
        return "".join(items)
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + ", and " + items[-1]


def category_colors(cfg: dict, cats: list[str]) -> dict:
    out = dict(cfg.get("categories") or {})
    for c in cats:
        if c not in out:
            out[c] = style.CATEGORY_PALETTE[len(out) % len(style.CATEGORY_PALETTE)]
    return {c: out[c] for c in list(cfg.get("categories") or {}) + cats if c in cats} or out


def crowded(points, w, h) -> bool:
    """True when labels would not fit: too many points or too much label text."""
    text = sum(style.text_width(str(p.get("label", "")), 6.6) for p in points)
    return len(points) > LAYOUT["max_labels"] or text > LAYOUT["label_budget"] * (w * h) / (372 * 392)


def chart_svg(points, colors, cfg, *, w, h, placeholder, sizes=False, wrap=22,
              numbered=False) -> str:
    if numbered:
        points = [dict(p, label="", marker_text=str(p.get("num", i))) for i, p in enumerate(points, 1)]
    c = qp.merge(qp.DEFAULTS, {
        "title": "", "x_label": "Effort to implement  \u2192",
        "y_label": "Impact on agent access  \u2192",
        "quadrants": dict(cfg["quadrants"]), "quadrant_colors": dict(style.QUADRANT_TINTS),
        "categories": colors, "width": w / 72, "height": h / 72, "dpi": 72,
        "dot_size": 70, "dot_edge_width": 1.2, "label_font_size": 6.6,
        "quadrant_font_size": 9.5, "axis_font_size": 7.5, "legend_font_size": 7,
        "label_color": style.INK, "quadrant_text_color": "#8A939C", "quadrant_text_alpha": 1,
        "axis_line_color": "#A3AAB1", "font_family": style.FONT, "background": style.PAGE,
        "avoid_overlap": True, "label_wrap": wrap, "size_range": [34, 360],
        "size_legend": sizes, "size_legend_title": "Repositories:" if sizes else "",
        "watermark": WATERMARK if placeholder else "", "watermark_alpha": 0.08,
        **({"dot_size": 125} if numbered else {}), "format": "svg",
    })
    import matplotlib.pyplot as plt
    with plt.rc_context({"svg.fonttype": "none"}):
        buf = io.StringIO()
        qp.plot(c, points, buf)
    svg = buf.getvalue()
    return svg[svg.index("<svg"):]


def chunk(seq, first, rest):
    out, i = [], 0
    while i < len(seq) or not out:
        n = first if not out else rest
        out.append(seq[i:i + n]); i += n
    return out


def chunk_by_height(rows, first_h, next_h, height):
    pages, cur, used, cap = [], [], 0.0, first_h
    for r in rows:
        h = height(r)
        if cur and used + h > cap:
            pages.append(cur); cur, used, cap = [], 0.0, next_h
        cur.append(r); used += h
    pages.append(cur)
    return pages


def fmt(v: float) -> str:
    return f"{v:+.2f}".replace("+0.00", "0.00").replace("-0.00", "0.00")


def build_context(run, cfg, work: Path, overrides_path: Path | None = None) -> dict:
    from .gaps import load_gaps
    slugs = [r.slug for r in run.repos]
    gapfiles = load_gaps(work, slugs)
    placements = load_placements(work, slugs)
    assessments = {s: json.loads((work / "assess" / f"{s}.json").read_text()) for s in slugs}
    overrides = load_overrides(overrides_path or work / "overrides.yaml")
    rub = load_rubric(cfg["rubric"])
    comb = combine(gapfiles, placements, cfg, overrides.get("combined"))

    cats = []
    for gf in gapfiles:
        for g in gf["gaps"]:
            if g["category"] not in cats:
                cats.append(g["category"])
    colors = category_colors(cfg, cats)
    placeholder = any(a["placeholder"] for a in assessments.values())
    backends = sorted({a["model"] for a in assessments.values() if a["placements"]}) or \
        sorted({a["model"] for a in assessments.values()})
    backend_label = "; ".join(backends)

    # ---- page 1 ---------------------------------------------------------
    n = comb["n_repos"]
    rows = comb["rows"]
    top = rows[0] if rows else None
    ties = [r for r in rows if top and r["count"] == top["count"]]
    for r in rows:
        r["fx"], r["fy"] = fmt(r["x"]), fmt(r["y"])
        r["color"] = colors.get(r["category"], "#444")
    ranked_pages = chunk(rows, LAYOUT["ranked_first"], LAYOUT["ranked_next"])
    qorder = [cfg["quadrants"][k] for k in ("top_left", "top_right", "bottom_left", "bottom_right")]
    by_quadrant = [{"name": q, "checks": sum(1 for r in rows if r["quadrant"] == q),
                    "gaps": sum(r["count"] for r in rows if r["quadrant"] == q)} for q in qorder]
    cards = [
        {"value": str(len(run.repos)), "label": f"repositories in the run"
         + (f", {n} with facet results" if n != len(run.repos) else "")},
        {"value": str(comb["total"]), "label": f"absent checks across {words(n)} "
         f"{plural(n, 'repository', 'repositories')}"},
        {"value": top["label"] if top else "none",
         "label": (f"absent in {top['count']} of {n}"
                   + (f"; tied with {words(len(ties) - 1)} other {plural(len(ties) - 1, 'check')}"
                      if len(ties) > 1 else "")) if top else "no absent checks in this run"},
    ]
    comb_numbered = len(comb["points"]) > LAYOUT["max_labels_combined"]
    for i, r in enumerate(rows, 1):
        r["num"] = i
    nums = {r["id"]: r["num"] for r in rows}
    for p in comb["points"]:
        p["num"] = nums.get(p["gap_id"])
    combined_svg = chart_svg(comb["points"], colors, cfg, w=LAYOUT["combined_w"],
                             h=LAYOUT["combined_h"], placeholder=placeholder, sizes=True,
                             wrap=24, numbered=comb_numbered) if comb["points"] else None

    # ---- repository pages ---------------------------------------------------
    repo_pages = []
    lh = 8.6
    for repo, gf in zip(run.repos, gapfiles):
        pl = placements[repo.slug]
        pts = pl.get("points") or []
        a = assessments[repo.slug]
        table = []
        pts = sorted(pts, key=lambda p: (-float(p["y"]), float(p["x"])))
        numbered = crowded(pts, LAYOUT["repo_w"], LAYOUT["repo_h"])
        for i, p in enumerate(pts, 1):
            table.append({"num": i,"label": p["label"], "check": p.get("check", ""),
                          "category": p["category"], "color": colors.get(p["category"], "#444"),
                          "fx": fmt(float(p["x"])), "fy": fmt(float(p["y"])),
                          "quadrant": p["quadrant"], "rationale": p.get("rationale", ""),
                          "confidence": p.get("confidence", ""),
                          "flag": "high variance" if p.get("high_variance") else
                                  ("edited" if p.get("overridden") else "")})
        src = gf["sources"].get("facet-check", {})
        available = any(s.get("available") for s in gf["sources"].values())
        non = gf["non_gaps"]
        non_text = join_and(f"{v} {k}" for k, v in non.items() if v)
        notes = []
        for s in gf["sources"].values():
            notes += s.get("notes") or []
        if repo.facet_exit not in (None, "0"):
            notes.insert(0, f"The facet Pi job exited {repo.facet_exit}; verdicts are from the "
                            "report it left.")

        def height(r, w=LAYOUT["rationale_w"]):
            head = style.line_count(f"{r['label']} ({r['check']}) {r['flag']}", 7.5, w)
            return 9 * head + 2 + lh * style.line_count(r["rationale"], 7, w) + 7.5
        L = LAYOUT
        banner_h = L["banner_small_h"] if a["placeholder"] else 0
        foot_h = L["foot_line"] * ((1 if non_text else 0) + len(notes)) + 8
        first_h = L["sheet_h"] - L["head_h"] - banner_h - L["th_h"] - 12
        next_h = L["sheet_h"] - L["head_h_next"] - banner_h - L["th_h"] - 12
        parts = chunk_by_height(table, first_h, next_h, height) if table else [[]]
        if len(parts) > 1:  # continuation pages use the full width
            rest = [r for p in parts[1:] for r in p]
            parts = [parts[0]] + chunk_by_height(
                rest, next_h, next_h, lambda r: height(r, L["rationale_w_full"]))
        svg = chart_svg(pts, colors, cfg, w=LAYOUT["repo_w"], h=LAYOUT["repo_h"],
                        placeholder=a["placeholder"], numbered=numbered) if pts else None
        k = len(gf["gaps"])
        if not available:
            caption = "No facet check results for this repository in the run, so nothing to place."
        elif k == 0:
            caption = "No check came back absent, so there is nothing to place."
        else:
            caption = (f"{words(k, True)} absent {plural(k, 'check')}, placed by "
                       f"{a['model']}. Sorted by impact."
                       + (" Numbers on the chart match the table." if numbered else ""))
        repo_pages.append({"name": repo.display, "full": repo.name, "url": repo.url,
                           "caption": caption, "svg": svg, "parts": parts, "k": k,
                           "available": available, "non_text": non_text, "notes": notes,
                           "hidden": max(0, k - len(pts)), "numbered": numbered})

    # ---- appendix: non-gap verdicts per check ---------------------------------
    checks, seen = [], {}
    for repo in run.repos:
        for row in repo.rows or []:
            ev = row["evaluation"]
            if ev not in seen:
                from .runfiles import category_label, check_label
                seen[ev] = {"label": check_label(ev), "category": category_label(row["property"]),
                            "counts": Counter()}
                checks.append(ev)
            seen[ev]["counts"][row["verdict"]] += 1
    verdict_cols = [v for v in VERDICTS if any(seen[c]["counts"][v] for c in checks)]
    vtable = [{"label": seen[c]["label"], "category": seen[c]["category"],
               "cells": [seen[c]["counts"][v] for v in verdict_cols]} for c in checks]

    acalls = sum(a["calls"] for a in assessments.values())
    hits = sum(a["cache_hits"] for a in assessments.values())
    samples = max((a["samples"] for a in assessments.values()), default=1)
    n_over = sum(len(v or {}) for v in (overrides.get("repos") or {}).values())
    hv = sum(1 for pl in placements.values() for p in pl.get("points") or [] if p.get("high_variance"))
    gap_verdicts = (cfg.get("gap_verdicts") or {}).get("facet-check", ["absent"])
    model_run = run.model or {}
    footer = f"{cfg['report']['org']}  \u00b7  {run.stamp}  \u00b7  " + \
        (f"placements: PLACEHOLDER ({', '.join(sorted({a['backend'] for a in assessments.values()}))})"
         if placeholder else f"placements: {backend_label}")
    rubric_tables = rub.tables()
    return {
        "title": cfg["report"]["title"], "footer": footer, "stamp": run.stamp,
        "stamp_text": run.stamp_text, "placeholder": placeholder, "backend": backend_label,
        "cards": cards, "comb_numbered": comb_numbered, "by_quadrant": by_quadrant, "combined_svg": combined_svg, "ranked_pages": ranked_pages,
        "n_repos": n, "n_checks": len(rows), "total": comb["total"], "repo_pages": repo_pages,
        "verdict_cols": [{"id": v, "fill": style.VERDICT_COLORS[v][0], "text": style.VERDICT_COLORS[v][1],
                          "sym": style.VERDICT_SYMBOLS[v]} for v in verdict_cols],
        "vtable": vtable, "gap_verdicts": join_and(gap_verdicts),
        "rubric": {"version": rub.version, "sha": rub.sha, "path": rub.path.name,
                   "x": rubric_tables.get("x: effort to implement", []),
                   "y": rubric_tables.get("y: impact on agent access", []),
                   "rules": rub.rules()},
        "method": {"calls": acalls, "hits": hits, "samples": samples, "overrides": n_over,
                   "high_variance": hv, "threshold": cfg["assess"]["variance_threshold"],
                   "sources": join_and(cfg.get("sources") or ["facet-check"]),
                   "run_model": " / ".join(v for v in (model_run.get("provider"), model_run.get("model")) if v) or "unknown",
                   "run_dir": run.dir.name},
        "colors": colors,
        "stub": any(a["backend"] == "stub" for a in assessments.values()),
        "subtitle": (f"Absent agent-access checks placed by effort and impact  \u00b7  "
                     f"run {run.stamp_text}"),
    }


def render(run, cfg, work: Path, pdf: Path, html: Path | None = None,
           overrides_path: Path | None = None) -> Path:
    ctx = build_context(run, cfg, work, overrides_path)
    env = Environment(loader=FileSystemLoader(str(ROOT / "templates")),
                      autoescape=select_autoescape(["html", "j2"]), undefined=StrictUndefined,
                      trim_blocks=True, lstrip_blocks=True)
    page = env.get_template("impact.html.j2").render(**ctx)
    pdf.parent.mkdir(parents=True, exist_ok=True)
    if html:
        html.write_text(page, encoding="utf-8")
    from weasyprint import HTML
    HTML(string=page, base_url=str(ROOT / "templates")).write_pdf(str(pdf))
    (work / "combined.json").write_text(json.dumps(
        {k: ctx[k] for k in ("stamp", "backend", "placeholder", "n_repos", "total")} |
        {"rows": [{k: r[k] for k in ("id", "label", "category", "count", "x", "y", "quadrant", "repos")}
                  for p in ctx["ranked_pages"] for r in p]}, indent=1) + "\n")
    return pdf
