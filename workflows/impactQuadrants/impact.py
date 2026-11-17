#!/usr/bin/env python3
"""impactQuadrants report: where to start on each repository's agent-access gaps.

    impact.py extract --run RUN_DIR                  # gaps/<repo>.json (no model)
    impact.py assess  --run RUN_DIR [--backend pi|openai|stub] [--samples 3]
    impact.py review  --run RUN_DIR                  # placements/<repo>.yaml + overrides.yaml
    impact.py report  --run RUN_DIR -o out/impact-<stamp>.pdf
    impact.py all     --run RUN_DIR --backend stub   # every step

RUN_DIR is workflows/repo_herd/runs/<UTC stamp>/. Intermediate files go to
--work (default: work/<stamp>/ next to this script). Nothing in RUN_DIR is changed.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from impactlib import assess as assess_mod  # noqa: E402
from impactlib import backends, config, gaps, report, review as review_mod  # noqa: E402
from impactlib import rubric as rubric_mod  # noqa: E402
from impactlib.runfiles import load_run  # noqa: E402


def log(msg: str) -> None:
    print(msg, file=sys.stderr)


def setup(a):
    cfg = config.load(a.config)
    if getattr(a, "sources", None):
        cfg["sources"] = [s.strip() for s in a.sources.split(",") if s.strip()]
    if getattr(a, "rubric", None):
        cfg["rubric"] = str(a.rubric)
    run = load_run(a.run, rename=cfg["report"].get("rename") or {})
    work = Path(a.work) if a.work else ROOT / "work" / run.stamp
    work.mkdir(parents=True, exist_ok=True)
    for w in run.warnings:
        log(f"warning: {w}")
    return cfg, run, work


def cmd_extract(a, cfg, run, work):
    paths = gaps.extract(run, cfg, work)
    total = 0
    for p in paths:
        d = json.loads(p.read_text())
        total += len(d["gaps"])
        log(f"{d['repo']['display']:>16}: {len(d['gaps'])} gaps  (not gaps: "
            + ", ".join(f"{v} {k}" for k, v in d["non_gaps"].items()) + ")")
    log(f"{total} gaps in {len(paths)} repositories -> {work / 'gaps'}")


def cmd_assess(a, cfg, run, work):
    name = a.backend or cfg.get("backend") or "pi"
    be = backends.make(name, cfg, model=a.model, provider=a.provider)
    rub = rubric_mod.load(cfg["rubric"])
    samples = a.samples or int(cfg["assess"]["samples"])
    if be.placeholder:
        log("NOTE: --backend stub writes PLACEHOLDER placements (not model output).")
    out = work / "assess"
    out.mkdir(parents=True, exist_ok=True)
    for gf in gaps.load_gaps(work, [r.slug for r in run.repos]):
        ctx = {}
        for s in gf["sources"].values():
            ctx.update(s.get("context") or {})
        res = assess_mod.assess_repo(gf, be, rub, cfg, work, samples, ctx, log=log)
        (out / f"{gf['repo']['slug']}.json").write_text(
            json.dumps(res, indent=1, ensure_ascii=False) + "\n")
        log(f"{gf['repo']['display']:>16}: {len(res['placements'])} placed "
            f"({res['calls']} calls, {res['cache_hits']} cached) via {be.label}")


def cmd_review(a, cfg, run, work):
    paths = review_mod.review(run, cfg, work, Path(a.overrides) if a.overrides else None, log=log)
    log(f"{len(paths)} placement files -> {work / 'placements'}")


def cmd_report(a, cfg, run, work):
    out = Path(a.output) if a.output else ROOT / "out" / f"impact-{run.stamp}.pdf"
    report.render(run, cfg, work, out, Path(a.html) if a.html else None,
                  Path(a.overrides) if a.overrides else None)
    print(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("extract", "assess", "review", "report", "all"):
        p = sub.add_parser(name)
        p.add_argument("--run", required=True, type=Path, help="repo_herd run folder")
        p.add_argument("--work", help="intermediate files (default work/<stamp>)")
        p.add_argument("--config", help="settings file (default impact.yaml)")
        p.add_argument("--sources", help="comma-separated gap sources (default from config)")
        if name in ("assess", "all"):
            p.add_argument("--backend", choices=sorted(backends.BACKENDS))
            p.add_argument("--model"); p.add_argument("--provider")
            p.add_argument("--samples", type=int)
            p.add_argument("--rubric", type=Path, help="rubric file (default rubric.md)")
        if name in ("review", "report", "all"):
            p.add_argument("--overrides", help="overrides file (default <work>/overrides.yaml)")
        if name in ("report", "all"):
            p.add_argument("-o", "--output", help="PDF path (default out/impact-<stamp>.pdf)")
            p.add_argument("--html", help="also write the HTML")
    a = ap.parse_args(argv)
    cfg, run, work = setup(a)
    steps = {"extract": [cmd_extract], "assess": [cmd_assess], "review": [cmd_review],
             "report": [cmd_report],
             "all": [cmd_extract, cmd_assess, cmd_review, cmd_report]}[a.cmd]
    for step in steps:
        step(a, cfg, run, work)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
