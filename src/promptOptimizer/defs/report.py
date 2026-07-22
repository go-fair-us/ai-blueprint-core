"""Render a human-readable markdown report of an optimization comparison.

Pulls the scoreboard from ``comparison-<task>.json`` (or accepts rows directly
from a just-finished ``compare`` run) and the before/after prompts from each
saved program, and writes ``report-<task>.md`` under the configured outputdir.
"""
from __future__ import annotations

import datetime
import difflib
import json
import os

from defs import paths as pathconf
from defs.prompts import optimized_prompt, seed_prompt

BRANCHES = ("baseline", "bootstrap", "mipro", "gepa")


def _load_comparison(task_name: str):
    path = pathconf.comparison_path(task_name)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def _demo_scenarios(demos, field="task_description") -> list[str]:
    out = []
    for d in demos:
        val = getattr(d, field, None)
        if val is None and hasattr(d, "get"):
            val = d.get(field)
        out.append(str(val)[:120] if val else "(demo)")
    return out


def _diff(seed_text: str, new_text: str) -> str:
    return "\n".join(
        difflib.unified_diff(
            seed_text.splitlines(), new_text.splitlines(),
            fromfile="seed", tofile="optimized", lineterm="",
        )
    )


def write_report(task, rows=None) -> str:
    """Write the markdown report and return its path.

    ``rows`` is a list of dicts (name, score, seconds, total_tokens, artifact)
    from a just-run comparison; if None, it's loaded from disk under outputdir.
    """
    if rows is None:
        rows = _load_comparison(task.name)

    seed = seed_prompt(task)
    seed_instr = (seed[0]["instructions"] if seed else "").strip()

    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    md = [
        f"# Prompt optimization report — profile `{task.name}`",
        "",
        f"*{task.description}*  ",
        f"Generated {stamp}",
        "",
        f"_outputdir: `{pathconf.OUTPUTDIR}`_",
        "",
        "## Results",
        "",
    ]

    if rows:
        rows = sorted(rows, key=lambda r: r.get("score", 0.0), reverse=True)
        md += [
            "| Rank | Optimizer | Score | Tokens | Cost ($) | Seconds | Artifact |",
            "|---|---|---:|---:|---:|---:|---|",
        ]
        for i, r in enumerate(rows, 1):
            md.append(
                f"| {i} | `{r.get('name', '?')}` | {r.get('score', 0):.3f} | "
                f"{r.get('total_tokens', 0):,} | {r.get('cost', 0.0):.4f} | {r.get('seconds', 0):.0f} | "
                f"`{os.path.basename(str(r.get('artifact', '')))}` |"
            )
        winner = rows[0]
        md += ["", f"**Winner: `{winner.get('name')}`** — score {winner.get('score', 0):.3f}."]
    else:
        md.append("_No comparison data found — run `compare` first for scores. "
                  "Showing whatever compiled prompts exist in outputdir._")
        rows = [
            {"name": b, "artifact": str(pathconf.program_path(task.name, b))}
            for b in BRANCHES
            if pathconf.program_path(task.name, b).exists()
        ]
    md.append("")

    md += [
        "## Seed prompt (hand-written)",
        "",
        "The starting instruction — the generation signature's docstring:",
        "",
        "```text",
        seed_instr or "(none)",
        "```",
        "",
        "## Optimized prompts",
        "",
    ]

    for r in rows:
        name = r.get("name", "?")
        path = r.get("artifact") or str(pathconf.program_path(task.name, name))
        if not os.path.exists(path):
            # Try bare name under outputdir
            alt = pathconf.program_path(task.name, name)
            if alt.exists():
                path = str(alt)
            else:
                continue
        try:
            opt = optimized_prompt(task, path)
        except Exception as e:
            md += [f"### `{name}`", "", f"_could not read {os.path.basename(path)}: {e}_", ""]
            continue
        instr = (opt[0]["instructions"] if opt else "").strip()
        demos = opt[0]["demos"] if opt else []

        md.append(f"### `{name}`")
        md.append("")
        score = r.get("score")
        meta = f"demos: **{len(demos)}**"
        if score is not None:
            meta = f"Score: **{score:.3f}**  ·  " + meta
        md += [meta, ""]

        if instr == seed_instr:
            md += ["_Instruction unchanged from seed._", ""]
        else:
            md += ["**Optimized instruction:**", "", "```text", instr, "```", ""]
            diff = _diff(seed_instr, instr)
            if diff:
                md += ["**Diff vs seed:**", "", "```diff", diff, "```", ""]

        if demos:
            md += ["**Few-shot demos (input scenarios):**", ""]
            md += [f"- {s}" for s in _demo_scenarios(demos)]
            md.append("")

    out = pathconf.report_path(task.name)
    out.write_text("\n".join(md), encoding="utf-8")
    return str(out)
