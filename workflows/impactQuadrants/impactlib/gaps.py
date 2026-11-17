"""Extract step: run folder -> gaps/<slug>.json (no model involved).

Gap item schema (schema/gap-item.schema.json), one per thing that could be fixed:
  id            "<source>:<key>", unique within a repository
  source        registered extractor name ("facet-check"; later "competency-question")
  key           stable id within the source (evaluation id) - the combined chart groups on it
  label         display name of the check / item
  category      free text (from the run); colours come from impact.yaml or a palette
  verdict       the source's verdict that made it a gap ("absent")
  evidence_url, evidence[], summary, report_gaps[], operator_fix, context{}
"""
from __future__ import annotations

import json
from pathlib import Path

from . import extractors
from .runfiles import VERDICTS, Run

SCHEMA = "impact-gaps/1"


def extract_repo(run: Run, repo, cfg) -> dict:
    out = {"schema": SCHEMA, "run": run.stamp,
           "repo": {"slug": repo.slug, "name": repo.name, "display": repo.display,
                    "url": repo.url, "facet_exit": repo.facet_exit},
           "gaps": [], "non_gaps": {}, "sources": {}}
    for src in cfg.get("sources") or ["facet-check"]:
        res = extractors.get(src)(run, repo, cfg)
        for g in res.gaps:
            if g.get("source") != src:
                raise ValueError(f"{src}: gap {g.get('id')} has source {g.get('source')!r}")
        out["gaps"] += res.gaps
        out["sources"][src] = {"available": res.available, "gaps": len(res.gaps),
                               "non_gaps": res.non_gaps, "notes": res.notes,
                               "context": res.context}
        for k, n in res.non_gaps.items():
            out["non_gaps"][k] = out["non_gaps"].get(k, 0) + n
    order = {v: i for i, v in enumerate(VERDICTS)}
    out["non_gaps"] = dict(sorted(out["non_gaps"].items(), key=lambda kv: order.get(kv[0], 99)))
    ids = [g["id"] for g in out["gaps"]]
    if len(ids) != len(set(ids)):
        raise ValueError(f"{repo.slug}: duplicate gap ids")
    return out


def extract(run: Run, cfg, work: Path) -> list[Path]:
    d = work / "gaps"
    d.mkdir(parents=True, exist_ok=True)
    paths = []
    for repo in run.repos:
        data = extract_repo(run, repo, cfg)
        p = d / f"{repo.slug}.json"
        p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        paths.append(p)
    (work / "run.json").write_text(json.dumps({
        "stamp": run.stamp, "run_dir": str(run.dir), "model": run.model,
        "repos": [r.slug for r in run.repos], "warnings": run.warnings}, indent=2) + "\n")
    return paths


def load_gaps(work: Path, slugs: list[str]) -> list[dict]:
    out = []
    for s in slugs:
        p = work / "gaps" / f"{s}.json"
        if not p.is_file():
            raise SystemExit(f"{p} missing; run `impact.py extract` first")
        out.append(json.loads(p.read_text(encoding="utf-8")))
    return out
