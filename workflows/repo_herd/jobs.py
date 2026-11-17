#!/usr/bin/env python3
"""Plan repository-herd jobs and score the reports those jobs write.

This file does not start Pi or Herdr. The shell driver is run-repo-herd.sh.
Answer keys are written beside each run for the grader. They are not copied
into the prompt.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

try:
    import yaml
except ImportError:  # pragma: no cover - the project venv provides PyYAML
    yaml = None  # type: ignore[assignment]


FACETS: tuple[tuple[str, str], ...] = (
    ("Be reachable", "reachable-fetch"),
    ("Be reachable", "robots-policy"),
    ("Be readable", "llms-txt"),
    ("Be readable", "sitemap"),
    ("Be readable", "server-rendered-content"),
    ("Be readable", "markdown-negotiation"),
    ("Be readable", "bulk-export"),
    ("Be readable", "agent-documentation"),
    ("Be callable", "openapi-discovery"),
    ("Be callable", "metadata-api"),
    ("Be callable", "api-http-behavior"),
    ("Be callable", "mcp-exposure"),
    ("Be meaningful", "dataset-jsonld"),
    ("Be meaningful", "persistent-identifiers"),
    ("Be meaningful", "vocabulary"),
    ("Be meaningful", "metadata-profile"),
    ("Be meaningful", "shacl-shapes"),
    ("Be meaningful", "sssom-mappings"),
    ("Be meaningful", "competency-questions"),
)

VERDICTS = {"present", "partial", "absent", "blocked", "not-observable"}
METABOLOMICS_HOST = "www.metabolomicsworkbench.org"
PRIOR_NOTES = (
    'read_prompt_file path "api_examples/MW_REST_API_NIAID_Blueprint_Compatibility.md" '
    "only as prior notes from October 2026. Re-test every claim against a response "
    "you receive in this run. A block recorded there is not today's verdict."
)
NO_PRIOR_NOTES = "There is no prior compatibility note for this origin. Skip this step."
SKIPPED_ANSWERABILITY = """# Answerability skipped

No single-host competency-question run is on file for this repository in `compQuestions/answerability_runs.md`.

The facet review still includes `evals/competency-questions.md`, which checks whether the site published its own list. This herd does not invent questions.
"""

FENCE_RE = re.compile(r"```yaml\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)
URL_RE = re.compile(r"https?://[^\s)>\"]+")
CONTAINS_RE = re.compile(
    r"^contains:\s*(?:'[^']*'|\"[^\"]*\")(?:\s+AND\s*(?:'[^']*'|\"[^\"]*\"))*$",
    re.IGNORECASE,
)
QUOTED_RE = re.compile(r"'([^']*)'|\"([^\"]*)\"")
EXACT_QUOTED_RE = re.compile(r"^exact(?:\s+on)?\s+(?:'([^']+)'|\"([^\"]+)\")$", re.IGNORECASE)
EXACT_TOKEN_RE = re.compile(r"^exact(?:\s+on)?\s+(\d[\w.-]*)$", re.IGNORECASE)
FLOOR_RE = re.compile(r"^numeric,\s*tolerance:.*accept\s*>=\s*(\d+)\s*$", re.IGNORECASE)


@dataclass
class Repo:
    community: str
    name: str
    url: str
    origin: str
    host: str
    hints: list[str]
    style: str
    open_web_search: str
    nde: str
    gds: str
    notes: str
    slug: str
    question_origin: str
    question_host: str
    alias_note: str = ""


@dataclass
class QuestionRun:
    section: str
    run: str
    origin: str
    host: str
    yaml_text: str
    key_table: str
    question_ids: list[str] = field(default_factory=list)


def host_of(url: str) -> str:
    parsed = urlparse(url.strip())
    return (parsed.hostname or "").lower().rstrip(".")


def origin_of(url: str) -> str:
    parsed = urlparse(url.strip())
    scheme = parsed.scheme or "https"
    host = (parsed.hostname or "").lower().rstrip(".")
    if not host:
        raise ValueError(f"URL has no host: {url}")
    return f"{scheme}://{host}/"


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.casefold()).strip("-")
    return slug[:60].strip("-") or "repository"


def hint_urls(url: str, additional: str) -> list[str]:
    """Pages other than the bare origin. A path on the CSV URL is a hint."""
    hints: list[str] = []
    parsed = urlparse(url.strip())
    path = parsed.path or ""
    if path not in ("", "/"):
        hints.append(url.strip())
    for token in (additional or "").split():
        if "://" in token and token not in hints:
            hints.append(token)
    return hints


def load_aliases(path: Path) -> dict[str, dict[str, str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"{path} must be a JSON object keyed by host")
    return data


def load_repos(csv_path: Path, aliases: dict[str, dict[str, str]], tokens: list[str]) -> list[Repo]:
    rows: list[Repo] = []
    with csv_path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        required = {"Name", "URL"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise SystemExit(f"{csv_path} is missing columns: {', '.join(sorted(missing))}")
        for raw in reader:
            name = (raw.get("Name") or "").strip()
            url = (raw.get("URL") or "").strip()
            if not name or not url:
                continue
            origin = origin_of(url)
            host = host_of(origin)
            alias = aliases.get(host, {})
            question_origin = (alias.get("question_origin") or origin).strip()
            rows.append(
                Repo(
                    community=(raw.get("Community") or "").strip(),
                    name=name,
                    url=url,
                    origin=origin,
                    host=host,
                    hints=hint_urls(url, raw.get("Additional Reference URL") or ""),
                    style=(raw.get("style") or "").strip(),
                    open_web_search=(raw.get("open web search") or "").strip(),
                    nde=(raw.get("NDE") or "").strip(),
                    gds=(raw.get("GDS") or "").strip(),
                    notes=(raw.get("Notes") or "").strip(),
                    slug=slugify(name),
                    question_origin=origin_of(question_origin),
                    question_host=host_of(question_origin),
                    alias_note=(alias.get("note") or "").strip(),
                )
            )
    seen: dict[str, str] = {}
    for repo in rows:
        previous = seen.get(repo.slug)
        if previous:
            raise SystemExit(f"Slug {repo.slug} is shared by {previous} and {repo.name}")
        seen[repo.slug] = repo.name
    if not tokens:
        return rows
    folded = [token.casefold() for token in tokens if token]
    selected = [repo for repo in rows if any(token in repo.name.casefold() for token in folded)]
    unmatched = [token for token in folded if not any(token in repo.name.casefold() for repo in rows)]
    if unmatched:
        raise SystemExit("No CSV Name contains: " + ", ".join(unmatched))
    return selected


def _section_spans(text: str) -> list[tuple[str, str]]:
    """Return (heading, body) for each `##` section. The heading has no hashes."""
    matches = list(re.finditer(r"^## (.+)$", text, re.MULTILINE))
    spans: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        spans.append((match.group(1).strip(), text[start:end]))
    return spans


def _run_spans(body: str) -> list[tuple[str, str]]:
    matches = list(re.finditer(r"^### (.+)$", body, re.MULTILINE))
    spans: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        spans.append((match.group(1).strip(), body[start:end]))
    return spans


def _key_table(run_body: str, fence_end: int) -> tuple[str, list[str]]:
    tail = run_body[fence_end:]
    lines = tail.splitlines()
    start = next((i for i, line in enumerate(lines) if line.startswith("| ID |")), None)
    if start is None:
        raise ValueError("answer-key table is missing")
    table: list[str] = []
    for line in lines[start:]:
        if not line.startswith("|"):
            break
        table.append(line)
    ids: list[str] = []
    for line in table[2:]:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and cells[0] and not set(cells[0]) <= set("-:"):
            ids.append(cells[0])
    return "\n".join(table) + "\n", ids


def normalize_question_yaml(yaml_text: str, section_origin: str, label: str) -> str:
    """Dump the question block with single-quoted scalars.

    One PlasmoDB question contains both quote characters. A Pi argument can
    keep that text for both of Pi's parsers when the YAML itself has no
    double quotes: the whole block is then one double-quoted argument, and
    the apostrophes need no backslash.
    """
    parser = _require_yaml()
    try:
        data = parser.safe_load(yaml_text)
    except parser.YAMLError as exc:
        raise SystemExit(f"{label}: question YAML did not parse: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("questions"), list):
        raise SystemExit(f"{label}: question YAML needs an origin and a questions list")
    if len(data["questions"]) > 3:
        raise SystemExit(f"{label} has {len(data['questions'])} questions; the cap is 3")
    if origin_of(str(data.get("origin") or "")) != section_origin:
        raise SystemExit(f"{label}: YAML origin does not match the section origin {section_origin}")
    dumped = parser.safe_dump(
        {"origin": section_origin, "questions": [str(item) for item in data["questions"]]},
        default_style="'",
        sort_keys=False,
        allow_unicode=True,
        width=10**6,
    )
    if '"' in dumped:
        raise SystemExit(f"{label}: normalized question YAML still contains a double quote")
    return dumped if dumped.endswith("\n") else dumped + "\n"


def load_question_runs(path: Path) -> list[QuestionRun]:
    text = path.read_text(encoding="utf-8")
    runs: list[QuestionRun] = []
    for heading, body in _section_spans(text):
        if heading.casefold().startswith("cross-repository"):
            continue
        origin_match = re.search(r"^Origin:\s*(\S+)", body, re.MULTILINE)
        if origin_match is None:
            continue
        section_origin = origin_of(origin_match.group(1))
        for run_heading, run_body in _run_spans(body):
            if not re.fullmatch(r"Run\s+[A-Z]", run_heading):
                continue
            if "needs" in run_heading.casefold():
                continue
            fences = list(FENCE_RE.finditer(run_body))
            if not fences:
                raise SystemExit(f"{heading} {run_heading} has no YAML fence")
            label = f"{heading} {run_heading}"
            yaml_text = normalize_question_yaml(fences[0].group(1), section_origin, label)
            try:
                table, ids = _key_table(run_body, fences[0].end())
            except ValueError as exc:
                raise SystemExit(f"{label}: {exc}") from exc
            runs.append(
                QuestionRun(
                    section=heading,
                    run=run_heading.split()[-1],
                    origin=section_origin,
                    host=host_of(section_origin),
                    yaml_text=yaml_text,
                    key_table=table,
                    question_ids=ids,
                )
            )
    return runs


def quote_for_pi(text: str) -> str:
    """Quote one Pi slash-command argument.

    Single quotes are used when the text has none. Pi's parser keeps the
    inside of a single-quoted argument as typed, including double quotes,
    backslashes, and newlines. A value that contains a single quote uses the
    double-quoted form from the Metabolomics answerability driver.
    """
    if "'" not in text:
        return "'" + text + "'"
    out = ['"']
    index = 0
    while index < len(text):
        char = text[index]
        if char == "\\" and index + 1 < len(text) and text[index + 1] == '"':
            out.append('\\\\"')
            index += 2
            continue
        if char == '"':
            out.append('\\"')
            index += 1
            continue
        if char == "\\" and index + 1 == len(text):
            out.append("\\\\")
            index += 1
            continue
        out.append(char)
        index += 1
    out.append('"')
    return "".join(out)


def parse_pi_args(args_string: str, *, honor_backslash: bool) -> list[str]:
    args: list[str] = []
    current: list[str] = []
    in_quote: str | None = None
    index = 0
    while index < len(args_string):
        char = args_string[index]
        if in_quote:
            if (
                honor_backslash
                and char == "\\"
                and index + 1 < len(args_string)
                and args_string[index + 1] == in_quote
            ):
                current.append(in_quote)
                index += 2
                continue
            if char == in_quote:
                in_quote = None
                index += 1
                continue
            current.append(char)
            index += 1
            continue
        if char in {'"', "'"}:
            in_quote = char
            index += 1
            continue
        if char.isspace():
            if current:
                args.append("".join(current))
                current = []
            index += 1
            continue
        current.append(char)
        index += 1
    if in_quote:
        raise ValueError("unclosed quote in Pi argument string")
    if current:
        args.append("".join(current))
    return args


def build_answerability_message(origin: str, yaml_text: str) -> str:
    body = yaml_text.strip("\n") + "\n"
    return f"/competency-answerability {origin} {quote_for_pi(body)}"


def render_facet_prompt(template: str, repo: Repo) -> str:
    if repo.hints:
        hint_lines = "\n".join(f"  - {url}" for url in repo.hints)
        hint_block = (
            "- Hint pages from the operator list. Confirm each with a live response. "
            "A hint may be an API document, a download page, or a deeper path, and it "
            "may not be a record:\n"
            f"{hint_lines}"
        )
    else:
        hint_block = "- Hint pages: none."
    prior = PRIOR_NOTES if repo.host == METABOLOMICS_HOST else NO_PRIOR_NOTES
    rendered = (
        template.replace("{{NAME}}", repo.name)
        .replace("{{ORIGIN}}", repo.origin)
        .replace("{{HOST}}", repo.host)
        .replace("{{HINT_BLOCK}}", hint_block)
        .replace("{{STEP_PRIOR_NOTES}}", prior)
    )
    leftover = re.findall(r"\{\{[A-Z0-9_]+\}\}", rendered)
    if leftover:
        raise SystemExit("Unfilled facet prompt placeholders: " + ", ".join(leftover))
    return rendered if rendered.endswith("\n") else rendered + "\n"


def _repo_record(repo: Repo) -> dict[str, object]:
    return {
        "community": repo.community,
        "name": repo.name,
        "url": repo.url,
        "origin": repo.origin,
        "host": repo.host,
        "hints": repo.hints,
        "style": repo.style,
        "open_web_search": repo.open_web_search,
        "nde": repo.nde,
        "gds": repo.gds,
        "notes": repo.notes,
        "slug": repo.slug,
        "question_origin": repo.question_origin,
        "question_host": repo.question_host,
        "alias_note": repo.alias_note,
    }


def prepare(
    *,
    csv_path: Path,
    questions_path: Path,
    aliases_path: Path,
    template_path: Path,
    out: Path,
    repos_filter: str = "",
    only: str = "all",
) -> dict[str, object]:
    if only not in {"all", "facet", "answerability"}:
        raise SystemExit("--only must be all, facet, or answerability")
    tokens = [part.strip() for part in repos_filter.split(",") if part.strip()]
    aliases = load_aliases(aliases_path)
    repos = load_repos(csv_path, aliases, tokens)
    question_runs = load_question_runs(questions_path)
    template = template_path.read_text(encoding="utf-8")
    by_host: dict[str, list[QuestionRun]] = {}
    for run in question_runs:
        by_host.setdefault(run.host, []).append(run)

    claimed: dict[str, str] = {}
    for repo in repos:
        previous = claimed.get(repo.question_host)
        if previous and previous != repo.name:
            raise SystemExit(
                f"Question host {repo.question_host} is claimed by {previous} and {repo.name}"
            )
        claimed[repo.question_host] = repo.name

    out.mkdir(parents=True, exist_ok=True)
    jobs: list[dict[str, object]] = []
    warnings: list[str] = []
    if not tokens:
        selected_hosts = {repo.question_host for repo in repos}
        for host, runs in by_host.items():
            if host not in selected_hosts:
                warnings.append(
                    f"No CSV row matches question host {host} ({runs[0].section})"
                )

    for repo in repos:
        repo_dir = out / repo.slug
        repo_dir.mkdir(parents=True, exist_ok=True)
        (repo_dir / "repo.json").write_text(
            json.dumps(_repo_record(repo), indent=2) + "\n",
            encoding="utf-8",
        )
        runs = by_host.get(repo.question_host, [])
        if only in {"all", "facet"}:
            facet_dir = repo_dir / "facet"
            facet_dir.mkdir(parents=True, exist_ok=True)
            prompt_rel = f"{repo.slug}/facet/prompt.txt"
            (out / prompt_rel).write_text(render_facet_prompt(template, repo), encoding="utf-8")
            jobs.append(
                {
                    "id": f"{repo.slug}-facet",
                    "kind": "facet",
                    "slug": repo.slug,
                    "name": repo.name,
                    "host": repo.host,
                    "origin": repo.origin,
                    "dir": f"{repo.slug}/facet",
                    "prompt": prompt_rel,
                    "run": None,
                    "question_ids": [],
                }
            )
        if runs and only in {"all", "answerability"}:
            for run in runs:
                run_dir = repo_dir / "answerability" / f"run-{run.run.lower()}"
                run_dir.mkdir(parents=True, exist_ok=True)
                (run_dir / "input.yaml").write_text(run.yaml_text, encoding="utf-8")
                message = build_answerability_message(run.origin, run.yaml_text)
                prompt_rel = f"{repo.slug}/answerability/run-{run.run.lower()}/prompt.txt"
                (out / prompt_rel).write_text(message, encoding="utf-8")
                key = (
                    "# Answer key\n\n"
                    "This file is for the grader. It is not part of the Pi prompt.\n\n"
                    f"{run.key_table}"
                )
                (run_dir / "key.md").write_text(key, encoding="utf-8")
                jobs.append(
                    {
                        "id": f"{repo.slug}-answerability-{run.run.lower()}",
                        "kind": "answerability",
                        "slug": repo.slug,
                        "name": repo.name,
                        "host": run.host,
                        "origin": run.origin,
                        "dir": f"{repo.slug}/answerability/run-{run.run.lower()}",
                        "prompt": prompt_rel,
                        "run": run.run,
                        "question_ids": run.question_ids,
                    }
                )
        if not runs:
            (repo_dir / "skipped-answerability.md").write_text(
                SKIPPED_ANSWERABILITY,
                encoding="utf-8",
            )

    manifest = {
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "csv": str(csv_path),
        "questions": str(questions_path),
        "only": only,
        "repos_filter": tokens,
        "warnings": warnings,
        "repos": [_repo_record(repo) for repo in repos],
        "jobs": jobs,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)
    return manifest


def _require_yaml():
    if yaml is None:
        raise SystemExit("PyYAML is required to read reports. Run this with: uv run python")
    return yaml


def load_report_docs(text: str) -> list[dict]:
    parser = _require_yaml()
    chunks = FENCE_RE.findall(text) or [text]
    docs: list[dict] = []
    for chunk in chunks:
        try:
            data = parser.safe_load(chunk)
        except parser.YAMLError:
            continue
        if isinstance(data, dict) and ("evaluation" in data or "checks" in data):
            docs.append(data)
    return docs


def first_url(value: object) -> str | None:
    if isinstance(value, str):
        match = URL_RE.search(value)
        if match:
            return match.group(0).rstrip(".,;")
        return None
    if isinstance(value, dict):
        url = value.get("url")
        if isinstance(url, str) and url.startswith(("http://", "https://")):
            return url
        for item in value.values():
            found = first_url(item)
            if found:
                return found
    if isinstance(value, list):
        for item in value:
            found = first_url(item)
            if found:
                return found
    return None


def evidence_url(doc: dict) -> str:
    checks = doc.get("checks")
    if isinstance(checks, list):
        for check in checks:
            if isinstance(check, dict):
                found = first_url(check.get("evidence"))
                if found:
                    return found
    found = first_url(doc.get("fetches"))
    if found:
        return found
    target = doc.get("target")
    if isinstance(target, str) and target.startswith(("http://", "https://")):
        return target
    return ""


def facet_rows(report_text: str | None, origin: str) -> list[dict[str, str]]:
    found: dict[str, dict] = {}
    if report_text:
        for doc in load_report_docs(report_text):
            name = doc.get("evaluation")
            if isinstance(name, str):
                found[name.strip()] = doc
    rows: list[dict[str, str]] = []
    for property_name, evaluation in FACETS:
        doc = found.get(evaluation)
        if doc is None:
            rows.append(
                {
                    "property": property_name,
                    "evaluation": evaluation,
                    "verdict": "not-observable",
                    "evidence_url": origin,
                    "note": "report did not include this evaluation",
                }
            )
            continue
        verdict = str(doc.get("verdict") or "").strip()
        if verdict not in VERDICTS:
            verdict = verdict or "not-observable"
        rows.append(
            {
                "property": property_name,
                "evaluation": evaluation,
                "verdict": verdict,
                "evidence_url": evidence_url(doc) or origin,
                "note": "",
            }
        )
    return rows


def parse_key_table(text: str) -> list[dict[str, str]]:
    raw = [line for line in text.splitlines() if line.startswith("|")]
    if not raw:
        return []
    header = [cell.strip() for cell in raw[0].strip().strip("|").split("|")]
    rows: list[dict[str, str]] = []
    for line in raw[1:]:
        if re.match(r"^\|\s*-+", line):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < len(header):
            cells += [""] * (len(header) - len(cells))
        row = dict(zip(header, cells))
        if row.get("ID"):
            rows.append(row)
    return rows


def grade_check(check: str, expected: str, answer: str | None) -> str:
    """Return match, miss, ungraded, or no-answer.

    A row is graded only when the whole Check cell is one literal rule:
    a contains list joined by AND, an exact token that also appears in the
    expected answer, or a numeric floor written as ``accept >= N``.
    """
    if answer is None or not str(answer).strip():
        return "no-answer"
    text = " ".join(check.split())
    answer_text = str(answer)

    floor = FLOOR_RE.fullmatch(text)
    if floor:
        numbers = re.findall(r"\d+", answer_text)
        if not numbers:
            return "miss"
        return "match" if int(numbers[0]) >= int(floor.group(1)) else "miss"

    if CONTAINS_RE.fullmatch(text):
        tokens = [a or b for a, b in QUOTED_RE.findall(text)]
        if tokens and all(token.casefold() in answer_text.casefold() for token in tokens):
            return "match"
        return "miss"

    exact = EXACT_QUOTED_RE.fullmatch(text)
    token = ""
    if exact:
        token = exact.group(1) or exact.group(2) or ""
    else:
        bare = EXACT_TOKEN_RE.fullmatch(text)
        if bare:
            token = bare.group(1)
    if token and token.casefold() in expected.casefold():
        return "match" if token in answer_text else "miss"
    return "ungraded"


def _answer_for_index(doc: dict | None, index: int) -> str | None:
    if doc is None:
        return None
    checks = doc.get("checks")
    if not isinstance(checks, list) or index >= len(checks):
        return None
    check = checks[index]
    if not isinstance(check, dict):
        return None
    answer = check.get("answer")
    if answer is None:
        return None
    return str(answer)


def _answerability_doc(report_text: str | None) -> dict | None:
    if not report_text:
        return None
    docs = load_report_docs(report_text)
    for doc in docs:
        if doc.get("evaluation") == "competency-answerability":
            return doc
    return docs[0] if docs else None


def score_run(run_dir: Path) -> list[dict[str, str]]:
    key_path = run_dir / "key.md"
    report_path = run_dir / "report.md"
    if not key_path.is_file():
        return []
    rows = parse_key_table(key_path.read_text(encoding="utf-8"))
    report_text = report_path.read_text(encoding="utf-8") if report_path.is_file() else None
    doc = _answerability_doc(report_text) if report_text else None
    if report_text is None:
        status_override = "no-report"
    else:
        status_override = ""
    graded: list[dict[str, str]] = []
    for index, row in enumerate(rows):
        answer = None if status_override else _answer_for_index(doc, index)
        check = row.get("Check", "")
        expected = row.get("Expected answer", "")
        grade = status_override or grade_check(check, expected, answer)
        graded.append(
            {
                "id": row.get("ID", ""),
                "stability": (row.get("Stability") or "").split()[0] if row.get("Stability") else "",
                "grade": grade,
                "expected": expected,
                "answer": "" if answer is None else answer.replace("\n", " "),
                "check": check,
            }
        )
    return graded


def _meta_exit(path: Path) -> str:
    if not path.is_file():
        return ""
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("exit_code="):
            return line.split("=", 1)[1].strip()
    return ""


def _markdown_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def finish(out: Path) -> str:
    manifest_path = out / "manifest.json"
    if not manifest_path.is_file():
        raise SystemExit(f"No manifest at {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    repos = manifest.get("repos") or []
    lines: list[str] = [
        "# Repository herd summary",
        "",
        f"Stamp directory: `{out}`",
        "",
    ]
    failures = 0
    for repo in repos:
        slug = repo["slug"]
        lines.append(f"## {repo['name']}")
        lines.append("")
        lines.append(f"Facet origin: {repo['origin']}")
        if repo.get("alias_note"):
            lines.append("")
            lines.append(str(repo["alias_note"]))
            lines.append("")
            lines.append(f"Question origin: {repo['question_origin']}")
        lines.append("")
        facet_report = out / slug / "facet" / "report.md"
        report_text = facet_report.read_text(encoding="utf-8") if facet_report.is_file() else None
        if report_text is None and (out / slug / "facet").is_dir():
            lines.append("No facet report was saved.")
            lines.append("")
        elif report_text is None:
            lines.append("This run did not include a facet job.")
            lines.append("")
        rows = facet_rows(report_text, repo["origin"]) if (out / slug / "facet").is_dir() else []
        if rows:
            lines.append("| # | Property | Evaluation | Verdict | Evidence URL |")
            lines.append("| --- | --- | --- | --- | --- |")
            for index, row in enumerate(rows, start=1):
                note = f" ({row['note']})" if row["note"] else ""
                lines.append(
                    "| {n} | {prop} | {ev} | {verdict}{note} | {url} |".format(
                        n=index,
                        prop=_markdown_cell(row["property"]),
                        ev=_markdown_cell(row["evaluation"]),
                        verdict=_markdown_cell(row["verdict"]),
                        note=_markdown_cell(note),
                        url=_markdown_cell(row["evidence_url"]),
                    )
                )
            lines.append("")
        facet_meta = _meta_exit(out / slug / "facet" / "meta.txt")
        if facet_meta and facet_meta != "0":
            failures += 1
            lines.append(f"Facet Pi exit code: {facet_meta}")
            lines.append("")

        answer_root = out / slug / "answerability"
        skipped = out / slug / "skipped-answerability.md"
        if answer_root.is_dir():
            score_lines = [
                f"# {repo['name']} answerability score",
                "",
                "A Pi exit of 0 means the process finished. A match means this script applied the check to `checks[].answer`.",
                "",
                "Ungraded means the Check cell is more specific than the three rules this script applies: a `contains` list joined by AND, an exact token that appears in the expected answer, or a numeric floor (`accept >= N`).",
                "",
            ]
            run_dirs = sorted(path for path in answer_root.iterdir() if path.is_dir())
            for run_dir in run_dirs:
                graded = score_run(run_dir)
                exit_code = _meta_exit(run_dir / "meta.txt")
                if exit_code and exit_code != "0":
                    failures += 1
                score_lines.append(f"## {run_dir.name}")
                score_lines.append("")
                if exit_code:
                    score_lines.append(f"Pi exit code: {exit_code}")
                    score_lines.append("")
                score_lines.append("| ID | Stability | Grade | Expected | Answer | Check |")
                score_lines.append("| --- | --- | --- | --- | --- | --- |")
                for row in graded:
                    score_lines.append(
                        "| {id} | {stability} | {grade} | {expected} | {answer} | {check} |".format(
                            id=_markdown_cell(row["id"]),
                            stability=_markdown_cell(row["stability"]),
                            grade=_markdown_cell(row["grade"]),
                            expected=_markdown_cell(row["expected"]),
                            answer=_markdown_cell(row["answer"]),
                            check=_markdown_cell(row["check"]),
                        )
                    )
                score_lines.append("")
            (answer_root / "score.md").write_text("\n".join(score_lines), encoding="utf-8")
            lines.append(f"Answerability score: `{slug}/answerability/score.md`")
            lines.append("")
        elif skipped.is_file():
            lines.append(
                "No single-host competency-question run is on file for this repository. "
                "The facet check `competency-questions` still asks whether the site published its own list."
            )
            lines.append("")

    lines.append(f"Pi processes with a non-zero exit code: {failures}")
    lines.append("")
    summary = "\n".join(lines)
    (out / "summary.md").write_text(summary, encoding="utf-8")
    return summary


def _cmd_prepare(args: argparse.Namespace) -> int:
    manifest = prepare(
        csv_path=Path(args.csv),
        questions_path=Path(args.questions),
        aliases_path=Path(args.aliases),
        template_path=Path(args.template),
        out=Path(args.out),
        repos_filter=args.repos or "",
        only=args.only,
    )
    jobs = manifest["jobs"]
    facet_count = sum(1 for job in jobs if job["kind"] == "facet")
    answer_count = sum(1 for job in jobs if job["kind"] == "answerability")
    skipped = sum(1 for repo in manifest["repos"] if not any(
        job["slug"] == repo["slug"] and job["kind"] == "answerability" for job in jobs
    ) and (Path(args.out) / repo["slug"] / "skipped-answerability.md").is_file())
    print(
        f"Prepared {facet_count} facet jobs, {answer_count} answerability jobs, "
        f"{skipped} repositories without a single-host test set."
    )
    print(f"Output: {args.out}")
    return 0


def _cmd_finish(args: argparse.Namespace) -> int:
    finish(Path(args.out))
    print(f"Summary: {args.out}/summary.md")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Plan and score repository-herd jobs.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    prepare_parser = sub.add_parser("prepare", help="Write prompts and the job manifest.")
    prepare_parser.add_argument("--csv", required=True)
    prepare_parser.add_argument("--questions", required=True)
    prepare_parser.add_argument("--aliases", required=True)
    prepare_parser.add_argument("--template", required=True)
    prepare_parser.add_argument("--out", required=True)
    prepare_parser.add_argument("--repos", default="")
    prepare_parser.add_argument("--only", default="all", choices=["all", "facet", "answerability"])
    prepare_parser.set_defaults(func=_cmd_prepare)

    finish_parser = sub.add_parser("finish", help="Write summary.md and answerability scores.")
    finish_parser.add_argument("--out", required=True)
    finish_parser.set_defaults(func=_cmd_finish)

    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
