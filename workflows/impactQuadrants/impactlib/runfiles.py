"""Readers for a repo_herd run folder (workflows/repo_herd/runs/<UTC stamp>/).

The summary.md and manifest.json parsing is copied from the report template's
tools/from_repo_herd.py (kept here so this program is self-contained).
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import yaml

UNPARSED_NOTE = "report did not include this evaluation"  # jobs.py facet_rows() note
FENCE_RE = re.compile(r"```ya?ml\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)
# All verdicts jobs.py can write, plus "unparsed" (summary row whose YAML block was missing).
VERDICTS = ["present", "partial", "absent", "blocked", "not-observable", "unparsed"]

# Short display names for jobs.py FACETS evaluation ids. Unknown ids are title-cased.
CHECK_LABELS = {
    "reachable-fetch": "Reachable fetch", "robots-policy": "Robots policy",
    "llms-txt": "llms.txt", "sitemap": "Sitemap",
    "server-rendered-content": "Server-rendered HTML",
    "markdown-negotiation": "Markdown negotiation", "bulk-export": "Bulk export",
    "agent-documentation": "Agent documentation", "openapi-discovery": "OpenAPI discovery",
    "metadata-api": "Metadata API", "api-http-behavior": "API HTTP behaviour",
    "mcp-exposure": "MCP exposure", "dataset-jsonld": "Dataset JSON-LD",
    "persistent-identifiers": "Persistent identifiers", "vocabulary": "Vocabulary",
    "metadata-profile": "Metadata profile", "shacl-shapes": "SHACL shapes",
    "sssom-mappings": "SSSOM mappings", "competency-questions": "Competency questions page",
}


def check_label(ev: str) -> str:
    return CHECK_LABELS.get(ev) or ev.replace("-", " ").capitalize()


def category_label(prop: str) -> str:
    """'Be reachable' -> 'Reachable' (any other property text is kept, capitalised)."""
    s = re.sub(r"^Be\s+", "", prop.strip(), flags=re.I).strip() or prop.strip()
    return s[:1].upper() + s[1:]


def parse_meta(text: str | None) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in (text or "").splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def parse_model(command: str | None) -> dict | None:
    """'... --provider nrp --model deepseek-v4-flash ...' -> {provider, model}."""
    if not command:
        return None
    first = command.splitlines()[0]
    prov = re.search(r"--provider[ =](\S+)", first)
    model = re.search(r"--models?[ =](\S+)", first)
    if not model:
        return None
    return {"provider": prov.group(1) if prov else None, "model": model.group(1)}


def split_row(line: str) -> list[str]:
    cells = re.split(r"(?<!\\)\|", line.strip().strip("|"))
    return [c.strip().replace("\\|", "|") for c in cells]


def parse_summary(text: str) -> dict[str, list[dict]]:
    """summary.md -> {repo name: [{n, property, evaluation, verdict, note, evidence_url}]}."""
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
        m = re.match(r"^(\S+)\s*(?:\((.*)\))?$", cells[3])
        verdict, note = (m.group(1), (m.group(2) or "").strip()) if m else (cells[3], "")
        if verdict == "not-observable" and note == UNPARSED_NOTE:
            verdict = "unparsed"
        out[current].append({"n": int(cells[0]), "property": cells[1], "evaluation": cells[2],
                             "verdict": verdict, "note": note,
                             "evidence_url": cells[4] if len(cells) > 4 else ""})
    return out


def display_name(name: str) -> str:
    """'AccessClinicalData@NIAID (ACDN)' -> 'ACDN'."""
    m = re.match(r"^.*\(([^()]+)\)\s*$", name)
    return m.group(1).strip() if m else name


def stamp_text(stamp: str) -> str:
    try:
        dt = datetime.strptime(stamp, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return stamp
    return f"{dt.day} {dt.strftime('%B %Y, %H:%M')} UTC"


def load_yaml_blocks(text: str) -> tuple[dict[str, dict], list[str]]:
    """Fenced YAML blocks that carry `evaluation:`; returns ({evaluation: doc}, [ids whose
    block is present but does not parse])."""
    docs: dict[str, dict] = {}
    broken: list[str] = []
    for chunk in FENCE_RE.findall(text or ""):
        try:
            data = yaml.safe_load(chunk)
        except yaml.YAMLError:
            m = re.search(r"^evaluation:\s*([\w.-]+)", chunk, re.M)
            if m:
                broken.append(m.group(1))
            continue
        if isinstance(data, dict) and isinstance(data.get("evaluation"), str):
            docs.setdefault(data["evaluation"].strip(), data)
    return docs, broken


def raw_block(text: str, evaluation: str) -> str | None:
    """The raw text of the fenced block for `evaluation` (used when it does not parse)."""
    for chunk in FENCE_RE.findall(text or ""):
        if re.search(rf"^evaluation:\s*{re.escape(evaluation)}\s*$", chunk, re.M):
            return chunk
    return None


@dataclass
class Repo:
    slug: str
    name: str
    display: str
    url: str | None
    rows: list[dict] | None          # summary.md rows, None when the repo has no section
    facet_exit: str | None = None
    facet_report: str | None = None
    raw: dict = field(default_factory=dict)   # manifest entry


@dataclass
class Run:
    dir: Path
    stamp: str
    repos: list[Repo]
    model: dict | None
    warnings: list[str]

    @property
    def stamp_text(self) -> str:
        return stamp_text(self.stamp)


def load_run(run_dir: Path | str, rename: dict | None = None) -> Run:
    run_dir = Path(run_dir)
    warnings: list[str] = []
    mf = run_dir / "manifest.json"
    if not mf.is_file():
        raise SystemExit(f"{run_dir}: no manifest.json; is this a repo_herd run folder?")
    manifest = json.loads(mf.read_text(encoding="utf-8"))
    entries = manifest.get("repos") or []
    if not entries:
        raise SystemExit(f"{mf} lists no repositories")
    sm = run_dir / "summary.md"
    summary = parse_summary(sm.read_text(encoding="utf-8")) if sm.is_file() else {}
    if not sm.is_file():
        warnings.append("summary.md is missing (run `jobs.py finish --out RUN_DIR`)")
    repos, model, used = [], None, set()
    for e in entries:
        slug, name = e.get("slug") or "", e.get("name") or e.get("slug") or "?"
        shown = (rename or {}).get(name) or display_name(name)
        if shown in used:
            shown = name
        used.add(shown)
        fdir = run_dir / slug / "facet"
        meta = parse_meta((fdir / "meta.txt").read_text() if (fdir / "meta.txt").is_file() else None)
        cmd = (fdir / "command.txt").read_text() if (fdir / "command.txt").is_file() else None
        model = model or parse_model(cmd)
        report = (fdir / "report.md").read_text(encoding="utf-8") if (fdir / "report.md").is_file() else None
        rows = summary.get(name)
        if rows is None and summary:
            warnings.append(f"{name}: no section in summary.md")
        repos.append(Repo(slug=slug, name=name, display=shown, url=e.get("origin") or e.get("url"),
                          rows=rows, facet_exit=meta.get("exit_code"), facet_report=report, raw=e))
    return Run(dir=run_dir, stamp=run_dir.resolve().name, repos=repos, model=model,
               warnings=warnings)
