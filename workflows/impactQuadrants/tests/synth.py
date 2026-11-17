"""Write small synthetic repo_herd run folders for tests and layout stress checks."""
from __future__ import annotations

import json
from pathlib import Path

DEFAULT_CHECKS = [
    ("Be reachable", "reachable-fetch"), ("Be reachable", "robots-policy"),
    ("Be readable", "llms-txt"), ("Be readable", "sitemap"),
    ("Be callable", "openapi-discovery"), ("Be callable", "mcp-exposure"),
    ("Be meaningful", "dataset-jsonld"), ("Be meaningful", "shacl-shapes"),
]


def block(ev: str, verdict: str, broken: bool = False) -> str:
    if broken:
        return (f"```yaml\nevaluation: {ev}\nverdict: {verdict}\nchecks:\n  - id: x\n"
                f"    evidence: \"unterminated: [oops\n   bad: : indent\n```\n")
    return (f"```yaml\nevaluation: {ev}\ntarget: https://example.org/\nverdict: {verdict}\n"
            f"checks:\n  - id: {ev}-found\n    result: fail\n"
            f"    evidence: \"GET https://example.org/{ev} -> 404\"\n"
            f"  - id: {ev}-ok\n    result: pass\n    evidence: \"fine\"\n"
            f"summary: \"{ev} is {verdict} in this synthetic run.\"\n"
            f"gaps:\n  - \"No {ev} artifact was found.\"\n```\n")


def write_run(root: Path, repos: list[dict], stamp: str = "20260101T000000Z",
              checks=DEFAULT_CHECKS) -> Path:
    """repos: [{name, slug, verdicts: {ev: verdict}, broken: [ev], in_summary: bool}]"""
    run = root / stamp
    run.mkdir(parents=True)
    manifest = {"repos": [], "jobs": []}
    summary = ["# Repository herd summary", ""]
    for r in repos:
        slug = r["slug"]
        manifest["repos"].append({"name": r["name"], "slug": slug,
                                  "origin": f"https://{slug}.example.org/"})
        fd = run / slug / "facet"
        fd.mkdir(parents=True)
        (fd / "meta.txt").write_text("exit_code=0\nseconds=60\n")
        (fd / "command.txt").write_text("bin/pi --print --provider nrp --model test-model -- <prompt.txt>\n")
        verdicts = r.get("verdicts", {})
        props = []
        for prop, _ in checks:
            if prop not in props:
                props.append(prop)
        md = [f"# {r['name']} review", ""]
        for prop in props:
            md += [f"## {prop}", "",
                   f"For {prop.lower()}, what an operator should fix next is to publish the "
                   f"missing artifacts at stable URLs and link them from the homepage.", ""]
            for p2, ev in checks:
                if p2 == prop and ev in verdicts:
                    md.append(block(ev, verdicts[ev], ev in r.get("broken", [])))
        (fd / "report.md").write_text("\n".join(md))
        if not r.get("in_summary", True):
            continue
        summary += [f"## {r['name']}", "", "| # | Property | Evaluation | Verdict | Evidence URL |",
                    "| --- | --- | --- | --- | --- |"]
        for i, (prop, ev) in enumerate(checks, 1):
            v = verdicts.get(ev)
            cell = v if v else "not-observable (report did not include this evaluation)"
            summary.append(f"| {i} | {prop} | {ev} | {cell} | https://{slug}.example.org/{ev} |")
        summary.append("")
    (run / "manifest.json").write_text(json.dumps(manifest, indent=1))
    (run / "summary.md").write_text("\n".join(summary))
    return run


def small_run(root: Path) -> Path:
    checks = DEFAULT_CHECKS + [("Be governed", "license-clarity")]
    return write_run(root, [
        {"name": "Alpha Repository (ALP)", "slug": "alpha",
         "verdicts": {"reachable-fetch": "present", "robots-policy": "absent", "llms-txt": "absent",
                      "sitemap": "partial", "openapi-discovery": "absent", "mcp-exposure": "blocked",
                      "dataset-jsonld": "absent", "shacl-shapes": "absent",
                      "license-clarity": "absent"},
         "broken": ["shacl-shapes"]},
        {"name": "Beta", "slug": "beta",
         "verdicts": {ev: "present" for _, ev in checks}},
        {"name": "Gamma", "slug": "gamma", "verdicts": {}, "in_summary": False},
        {"name": "Delta (DEL)", "slug": "delta",
         "verdicts": {"llms-txt": "absent", "openapi-discovery": "absent",
                      "mcp-exposure": "absent", "sitemap": "not-observable"}},
    ], checks=checks)
