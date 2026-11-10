#!/usr/bin/env python3
"""Prepare, quote, and grade Metabolomics Workbench answerability runs.

The shell driver is run-metabolomics-answerability.sh. This file does not
call Pi. It extracts the fenced YAML the agent is allowed to see, builds the
/competency-answerability message, and scores a saved report against the
answer key.

The key stays here. Do not pass this file, or score.json, into the Pi run.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ORIGIN = "https://www.metabolomicsworkbench.org/"
SOURCE_NAME = "metabolomics-workbench-competency-questions-final.md"
RUNS = ("A", "B", "C", "D")

# Check text is the question-level rule in the source markdown.
# kind selects the matcher applied to the agent's answer field.
KEYS: dict[str, list[dict[str, object]]] = {
    "A": [
        {
            "id": "MW-1",
            "stability": "stable",
            "expected": "Fatb Induction Experiment (FatBIE); Arabidopsis thaliana",
            "check": "contains: 'FatBIE' AND 'Arabidopsis thaliana'",
            "kind": "contains",
            "parts": ["FatBIE", "Arabidopsis thaliana"],
            "anchor": "study title",
            "support": "GET https://www.metabolomicsworkbench.org/rest/study/study_id/ST000001/summary",
        },
        {
            "id": "MW-3",
            "stability": "stable",
            "expected": "pubchem_cid 5997; InChIKey HVYWMOMLDIMFJA-DPAQBDIFSA-N; refmet_id RM0135639",
            "check": "exact on '5997'; contains: 'HVYWMOMLDIMFJA-DPAQBDIFSA-N' AND 'RM0135639'",
            "kind": "token_and_contains",
            "token": "5997",
            "parts": ["HVYWMOMLDIMFJA-DPAQBDIFSA-N", "RM0135639"],
            "anchor": "Cholesterol",
            "support": "GET https://www.metabolomicsworkbench.org/rest/refmet/name/Cholesterol/all",
        },
        {
            "id": "MW-4",
            "stability": "stable",
            "expected": "Citric acid",
            "check": "exact (case-insensitive) on 'Citric acid'",
            "kind": "exact_ci",
            "parts": ["Citric acid"],
            "anchor": "citrate",
            "support": "GET https://www.metabolomicsworkbench.org/rest/refmet/match/citrate/name/",
        },
    ],
    "B": [
        {
            "id": "MW-2",
            "stability": "stable",
            "expected": "CC BY-NC-ND; https://creativecommons.org/licenses/by-nc-nd/4.0/deed.en",
            "check": "contains: 'CC BY-NC-ND' AND 'creativecommons.org/licenses/by-nc-nd/4.0'",
            "kind": "contains",
            "parts": ["CC BY-NC-ND", "creativecommons.org/licenses/by-nc-nd/4.0"],
            "anchor": "license",
            "support": "GET https://www.metabolomicsworkbench.org/rest/study/study_id/ST000001/summary",
        },
        {
            "id": "MW-5",
            "stability": "stable",
            "expected": "760.585077; C42H83NO8P",
            "check": "exact on 760.585077; contains: 'C42H83NO8P'",
            "kind": "token_and_contains",
            "token": "760.585077",
            "parts": ["C42H83NO8P"],
            "anchor": "PC(34:1)",
            "support": "GET https://www.metabolomicsworkbench.org/rest/moverz/exactmass/PC(34:1)/M%2BH",
        },
        {
            "id": "MW-6",
            "stability": "semi-stable",
            "expected": "102",
            "check": "numeric exact 102 (may change if the study is revised)",
            "kind": "numeric",
            "token": "102",
            "parts": [],
            "anchor": "named metabolites",
            "support": "GET https://www.metabolomicsworkbench.org/rest/study/study_id/ST000001/number_of_metabolites/",
        },
    ],
    "C": [
        {
            "id": "MW-7",
            "stability": "semi-stable",
            "expected": "5-Hydroxyculmorin and Hydroxypentadecadienoic acid; 255.1955",
            "check": "contains: '5-Hydroxyculmorin' AND 'Hydroxypentadecadienoic acid' AND '255.1955'",
            "kind": "contains",
            "parts": ["5-Hydroxyculmorin", "Hydroxypentadecadienoic acid", "255.1955"],
            "anchor": "255.2",
            "support": "GET https://www.metabolomicsworkbench.org/rest/moverz/REFMET/255.2/M%2BH/0.2/txt",
        },
        {
            "id": "MW-8",
            "stability": "semi-stable",
            "expected": "C69H118O5; yes. DG 66:8 is among the closest matches",
            "check": "contains: 'C69H118O5' AND 'DG 66:8'",
            "kind": "contains",
            "parts": ["C69H118O5", "DG 66:8"],
            "anchor": "513.45",
            "support": "GET https://www.metabolomicsworkbench.org/rest/moverz/LIPIDS/513.45/M-2H/0.2/txt",
        },
        {
            "id": "MW-9",
            "stability": "semi-stable",
            "expected": "EC-18",
            "check": "contains: 'EC-18'",
            "kind": "contains",
            "parts": ["EC-18"],
            "anchor": "635.52",
            "support": "GET https://www.metabolomicsworkbench.org/rest/moverz/MB/635.52/M%2BH/0.5/txt",
        },
    ],
    "D": [
        {
            "id": "MW-10",
            "stability": "stable",
            "expected": "Diet:Pooled_All 3; Diet:Pooled_Prudent 3; Diet:Pooled_Western 3; Diet:Prudent_611 13; Diet:Western_907 8",
            "check": "contains the five group names and those counts",
            "kind": "factors",
            "parts": [
                "Diet:Pooled_All 3",
                "Diet:Pooled_Prudent 3",
                "Diet:Pooled_Western 3",
                "Diet:Prudent_611 13",
                "Diet:Western_907 8",
            ],
            "anchor": "AN000113",
            "support": "GET https://www.metabolomicsworkbench.org/rest/study/analysis_id/AN000113/untarg_factors/",
        },
        {
            "id": "MW-11",
            "stability": "stable",
            "expected": "Dideoxymycobactin",
            "check": "exact (case-insensitive) on 'Dideoxymycobactin'",
            "kind": "exact_ci",
            "parts": ["Dideoxymycobactin"],
            "anchor": "regno 11",
            "support": "GET https://www.metabolomicsworkbench.org/rest/compound/regno/11/name",
        },
    ],
}


def source_path(repo: Path) -> Path:
    return repo / "compQuestions" / "metabolomics" / SOURCE_NAME


def extract_runs(markdown: str) -> dict[str, str]:
    """Return the fenced YAML body for each Run A–D heading."""
    found: dict[str, str] = {}
    for match in re.finditer(
        r"^### Run ([A-D])\n.*?^```yaml\n(.*?)```",
        markdown,
        flags=re.M | re.S,
    ):
        found[match.group(1)] = match.group(2).strip("\n") + "\n"
    missing = [name for name in RUNS if name not in found]
    if missing:
        raise SystemExit(f"missing YAML fence for run(s): {', '.join(missing)}")
    return found


def question_lines(yaml_text: str) -> list[str]:
    lines = []
    for line in yaml_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            lines.append(stripped[2:].strip().strip('"'))
    return lines


def quote_for_pi(text: str) -> str:
    """Quote one Pi slash-command argument.

    Single quotes are used when the text has none. Pi's parser keeps the
    inside of a single-quoted argument as typed, including double quotes,
    backslashes, and newlines. That matches both the documented parser and
    the older parser that does not treat backslash as an escape.
    """
    if "'" in text:
        return _quote_double(text)
    return "'" + text + "'"


def _quote_double(text: str) -> str:
    """Double-quote for the documented Pi parser.

    A backslash escapes only the surrounding quote character. Any other
    backslash is kept. `\"` in the value is therefore written as `\\\"`.
    """
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


def build_message(origin: str, yaml_text: str) -> str:
    body = yaml_text.strip("\n") + "\n"
    return f"/competency-answerability {origin} {quote_for_pi(body)}"


def command_argv_roundtrip(message: str, origin: str, yaml_text: str) -> None:
    expected = yaml_text.strip("\n") + "\n"
    prefix = "/competency-answerability "
    if not message.startswith(prefix):
        raise AssertionError("message does not start with the slash command")
    for honor in (True, False):
        args = parse_pi_args(message[len(prefix) :], honor_backslash=honor)
        if args != [origin, expected]:
            raise AssertionError(
                f"Pi arg roundtrip failed (honor_backslash={honor}): {args[:1]}"
            )


def has_token(text: str, token: str) -> bool:
    if re.fullmatch(r"\d+", token):
        return re.search(rf"(?<!\d){re.escape(token)}(?!\d)", text) is not None
    return re.search(rf"(?<![\w.]){re.escape(token)}(?![\w.])", text) is not None


def exact_ci(text: str, expected: str) -> bool:
    cleaned = re.sub(r"\s+", " ", text).strip().strip("`").strip()
    if len(cleaned) >= 2 and cleaned[0] == cleaned[-1] and cleaned[0] in "'\"":
        cleaned = cleaned[1:-1].strip()
    cleaned = cleaned.rstrip(".").strip()
    return cleaned.casefold() == expected.casefold()


def factor_pair(text: str, name: str, count: str) -> bool:
    for match in re.finditer(re.escape(name), text):
        start = max(0, match.start() - 40)
        window = text[start : match.end() + 40]
        if re.search(rf"(?<!\d){re.escape(count)}(?!\d)", window):
            return True
    return False


def evidence_matches(spec: dict[str, object], text: str) -> bool:
    """Whether the quote contains the expected value.

    Exact answer rows still pass here when the name appears inside a longer
    quote. The answer field itself stays on the strict check.
    """
    if spec["kind"] == "exact_ci":
        return str(spec["parts"][0]).casefold() in text.casefold()
    return key_matches(spec, text)


def key_matches(spec: dict[str, object], text: str) -> bool:
    if text is None:
        return False
    kind = spec["kind"]
    parts = list(spec.get("parts") or [])
    if kind == "contains":
        return all(part in text for part in parts)
    if kind == "exact_ci":
        return exact_ci(text, str(parts[0]))
    if kind == "numeric":
        return has_token(text, str(spec["token"]))
    if kind == "token_and_contains":
        return has_token(text, str(spec["token"])) and all(part in text for part in parts)
    if kind == "factors":
        return all(factor_pair(text, name, count) for name, count in (part.rsplit(" ", 1) for part in parts))
    raise ValueError(f"unknown check kind: {kind}")


def last_yaml_document(text: str) -> str:
    fences = re.findall(r"```(?:yaml|yml)?[^\n]*\n(.*?)```", text, flags=re.S | re.I)
    for block in reversed(fences):
        if "evaluation:" in block or "checks:" in block:
            return block
    if fences:
        return fences[-1]
    marker = "\nevaluation:"
    index = text.rfind(marker)
    if index != -1:
        return text[index + 1 :]
    if text.lstrip().startswith("evaluation:"):
        return text
    return text


def _unquote(raw: str) -> str:
    value = raw.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        body = value[1:-1]
        if value[0] == '"':
            body = body.replace(r"\"", '"').replace(r"\n", "\n")
        return body
    return value


def parse_report(text: str) -> dict[str, object]:
    """Pull verdict and checks out of the model's YAML report."""
    body = last_yaml_document(text)
    verdict = None
    verdict_match = re.search(r"(?m)^verdict:\s*(\S+)", body)
    if verdict_match:
        verdict = verdict_match.group(1).strip("'\"")
    checks: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    active_key: str | None = None
    folded: list[str] = []

    def finish_fold() -> None:
        nonlocal active_key, folded
        if current is not None and active_key is not None:
            current[active_key] = "\n".join(folded).strip()
        active_key = None
        folded = []

    for line in body.splitlines():
        if active_key and (line.startswith("      ") or line.strip() == ""):
            folded.append(line[6:] if line.startswith("      ") else "")
            continue
        if active_key:
            finish_fold()
        if re.match(r"^\s*-\s+id:\s*", line):
            if current:
                checks.append(current)
            current = {"id": _unquote(line.split(":", 1)[1])}
            continue
        if current is None:
            continue
        item = re.match(
            r"^    (id|question|result|answer|evidence):\s*(.*)$",
            line,
        )
        if not item:
            continue
        key, raw = item.group(1), item.group(2).strip()
        if raw in {">", "|", ">-", "|-", ">+", "|+", ""}:
            active_key = key
            folded = []
            current[key] = ""
        else:
            current[key] = _unquote(raw)
    if active_key:
        finish_fold()
    if current:
        checks.append(current)
    return {"verdict": verdict, "checks": checks, "yaml": body}


def _assign_checks(
    specs: list[dict[str, object]],
    checks: list[dict[str, str]],
) -> list[tuple[dict[str, object], dict[str, str] | None]]:
    unused = list(checks)
    assigned: list[dict[str, str] | None] = [None] * len(specs)
    for index, spec in enumerate(specs):
        anchor = str(spec["anchor"]).casefold()
        for check in unused:
            if anchor in check.get("question", "").casefold():
                assigned[index] = check
                unused.remove(check)
                break
    for index in range(len(specs)):
        if assigned[index] is None and unused:
            assigned[index] = unused.pop(0)
    return list(zip(specs, assigned))


def grade_run(run: str, report_text: str | None) -> dict[str, object]:
    specs = KEYS[run]
    if report_text is None:
        return {
            "run": run,
            "verdict": None,
            "parse_note": "no report file",
            "questions": [_blank_question(spec) for spec in specs],
        }
    parsed = parse_report(report_text)
    questions = []
    for spec, check in _assign_checks(specs, list(parsed["checks"])):  # type: ignore[arg-type]
        answer = (check or {}).get("answer", "")
        evidence = (check or {}).get("evidence", "")
        questions.append(
            {
                "id": spec["id"],
                "stability": spec["stability"],
                "expected": spec["expected"],
                "check": spec["check"],
                "support": spec["support"],
                "procedure_result": (check or {}).get("result"),
                "question": (check or {}).get("question"),
                "agent_answer": answer or None,
                "key_match": key_matches(spec, answer or ""),
                "evidence_match": evidence_matches(spec, evidence or ""),
            }
        )
    note = None
    if not parsed["checks"]:
        note = "no checks parsed from the report; see report.md and llm-grade.md"
    return {
        "run": run,
        "verdict": parsed["verdict"],
        "parse_note": note,
        "questions": questions,
    }


def _blank_question(spec: dict[str, object]) -> dict[str, object]:
    return {
        "id": spec["id"],
        "stability": spec["stability"],
        "expected": spec["expected"],
        "check": spec["check"],
        "support": spec["support"],
        "procedure_result": None,
        "question": None,
        "agent_answer": None,
        "key_match": False,
        "evidence_match": False,
    }


def grade_directory(out: Path) -> dict[str, object]:
    runs = []
    for name in RUNS:
        run_dir = out / f"run-{name.lower()}"
        if not run_dir.is_dir():
            continue
        report = run_dir / "report.md"
        text = report.read_text(encoding="utf-8") if report.is_file() else None
        if text is not None and not text.strip():
            text = None
        graded = grade_run(name, text)
        meta_path = out / f"run-{name.lower()}" / "meta.txt"
        if meta_path.is_file():
            graded["meta"] = meta_path.read_text(encoding="utf-8").strip()
        runs.append(graded)
    questions = [question for run in runs for question in run["questions"]]
    matched = sum(1 for question in questions if question["key_match"])
    return {
        "origin": ORIGIN,
        "key_match": matched,
        "key_total": len(questions),
        "runs": runs,
    }


def render_score_md(score: dict[str, object]) -> str:
    lines = [
        "# Metabolomics Workbench answerability score",
        "",
        "Procedure result is the agent's own `pass` / `fail` / `not-observable`. That only means it quoted something it fetched. Key match is this script applying the check to the `answer` field.",
        "",
        f"Key match: {score['key_match']} / {score['key_total']}",
        "",
        "| Run | ID | Stability | Procedure | Key | Evidence has it | Answer |",
        "|---|---|---|---|---|---|---|",
    ]
    for run in score["runs"]:  # type: ignore[union-attr]
        for question in run["questions"]:
            answer = question.get("agent_answer") or ""
            answer = re.sub(r"\s+", " ", str(answer))
            if len(answer) > 80:
                answer = answer[:77] + "..."
            answer = answer.replace("|", "\\|")
            lines.append(
                "| {run} | {id} | {stability} | {procedure} | {key} | {evidence} | {answer} |".format(
                    run=run["run"],
                    id=question["id"],
                    stability=question["stability"],
                    procedure=question.get("procedure_result") or "—",
                    key="match" if question["key_match"] else "miss",
                    evidence="yes" if question["evidence_match"] else "no",
                    answer=answer or "—",
                )
            )
        if run.get("parse_note"):
            lines.append("")
            lines.append(f"Run {run['run']}: {run['parse_note']}.")
            lines.append("")
    lines.append("")
    lines.append("Semi-stable rows (MW-6, MW-7, MW-8, MW-9) can miss because the repository changed the record. Re-fetch the support URL in score.json before treating that miss as a model error.")
    lines.append("")
    lines.append("Exact rows (MW-4, MW-11) fail when the answer field adds words around the name. If Evidence has it is yes, read the quote before counting a hard miss.")
    lines.append("")
    return "\n".join(lines)


def render_llm_grade(score: dict[str, object], out: Path) -> str:
    parts = [
        "# Grade these answerability reports",
        "",
        "You are the grader. Do not fetch pages and do not answer the questions yourself.",
        "The agent was not supposed to see this key. Score only the saved report.",
        "",
        "For each question, decide whether the agent's answer satisfies the check.",
        "The procedure verdict is not the grade. An agent can mark `pass` and still be wrong.",
        "A deterministic pre-score is included. Override it when the answer is right but phrased differently, and say why.",
        "For a semi-stable miss, say that the support URL should be re-fetched before the miss is blamed on the model.",
        "",
        "Return one YAML document:",
        "",
        "```yaml",
        "key_match: <count>",
        "key_total: <count>",
        "scores:",
        "  - id: MW-1",
        "    match: true",
        "    reason: <one sentence>",
        "```",
        "",
        f"Deterministic pre-score: {score['key_match']} / {score['key_total']}",
        "",
    ]
    for run in score["runs"]:  # type: ignore[union-attr]
        report = out / f"run-{run['run'].lower()}" / "report.md"
        parts.append(f"## Run {run['run']}")
        parts.append("")
        parts.append(f"Procedure verdict parsed from the report: {run.get('verdict')}")
        parts.append("")
        for question in run["questions"]:
            parts.append(f"### {question['id']} ({question['stability']})")
            parts.append("")
            parts.append(f"Expected: {question['expected']}")
            parts.append(f"Check: {question['check']}")
            parts.append(f"Support, for a human re-check: {question['support']}")
            parts.append(f"Procedure result: {question.get('procedure_result')}")
            parts.append(f"Agent answer: {question.get('agent_answer')}")
            parts.append(
                f"Deterministic key match: {'match' if question['key_match'] else 'miss'}"
            )
            parts.append("")
        if report.is_file():
            parts.append("<report>")
            parts.append(report.read_text(encoding="utf-8").rstrip())
            parts.append("</report>")
            parts.append("")
    return "\n".join(parts)


def write_grade(out: Path) -> dict[str, object]:
    score = grade_directory(out)
    (out / "score.json").write_text(
        json.dumps(score, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (out / "score.md").write_text(render_score_md(score), encoding="utf-8")
    (out / "llm-grade.md").write_text(render_llm_grade(score, out), encoding="utf-8")
    return score


def prepare(source: Path, out: Path, runs: list[str]) -> None:
    extracted = extract_runs(source.read_text(encoding="utf-8"))
    for name in runs:
        if name not in extracted:
            raise SystemExit(f"unknown run {name}")
        run_dir = out / f"run-{name.lower()}"
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "input.yaml").write_text(extracted[name], encoding="utf-8")
        message = build_message(ORIGIN, extracted[name])
        command_argv_roundtrip(message, ORIGIN, extracted[name])
        (run_dir / "prompt.txt").write_text(message + "\n", encoding="utf-8")


def markdown_expected_answers(markdown: str) -> dict[str, str]:
    found: dict[str, str] = {}
    for match in re.finditer(
        r"^### (MW-\d+).*\n(?:.*\n)*?\*\*Expected answer:\*\* (.+)$",
        markdown,
        flags=re.M,
    ):
        found[match.group(1)] = match.group(2).strip()
    return found


def self_test(repo: Path) -> None:
    markdown = source_path(repo).read_text(encoding="utf-8")
    extracted = extract_runs(markdown)
    counts = {name: len(question_lines(extracted[name])) for name in RUNS}
    if counts != {"A": 3, "B": 3, "C": 3, "D": 2}:
        raise SystemExit(f"unexpected question counts: {counts}")
    for name in RUNS:
        if "'" in extracted[name]:
            raise SystemExit(f"run {name} YAML now contains a single quote; re-check quoting")
        message = build_message(ORIGIN, extracted[name])
        command_argv_roundtrip(message, ORIGIN, extracted[name])
    expected = markdown_expected_answers(markdown)
    for specs in KEYS.values():
        for spec in specs:
            text = expected.get(str(spec["id"]))
            if not text:
                raise SystemExit(f"missing expected answer for {spec['id']}")
            needle = str(spec["parts"][0]) if spec["kind"] != "numeric" else str(spec["token"])
            if needle not in text and str(spec["expected"]) not in text:
                raise SystemExit(f"key drifted from markdown for {spec['id']}")

    sample = """```yaml
evaluation: competency-answerability
target: https://www.metabolomicsworkbench.org/
verdict: partial
checks:
  - id: q1
    question: "What is the study title and species of Metabolomics Workbench study ST000001?"
    result: pass
    answer: "Fatb Induction Experiment (FatBIE); Arabidopsis thaliana"
    evidence: "study_title Fatb Induction Experiment (FatBIE); species Arabidopsis thaliana"
  - id: q2
    question: "What PubChem CID, InChIKey, and RefMet ID does Metabolomics Workbench RefMet assign to Cholesterol?"
    result: pass
    answer: "5997 / HVYWMOMLDIMFJA-DPAQBDIFSA-N / RM0135639"
    evidence: "same"
  - id: q3
    question: "What official RefMet name does the Metabolomics Workbench REST service return when matching the synonym \\"citrate\\"?"
    result: pass
    answer: "The name is Citric acid"
    evidence: "refmet_name: Citric acid"
```
"""
    graded = grade_run("A", sample)
    by_id = {row["id"]: row for row in graded["questions"]}  # type: ignore[index]
    if graded["verdict"] != "partial":
        raise SystemExit(f"verdict parse failed: {graded['verdict']}")
    if not by_id["MW-1"]["key_match"] or not by_id["MW-3"]["key_match"]:
        raise SystemExit(f"expected MW-1 and MW-3 to match: {by_id}")
    if by_id["MW-4"]["key_match"] or not by_id["MW-4"]["evidence_match"]:
        raise SystemExit(f"MW-4 exact versus evidence failed: {by_id['MW-4']}")

    factors = "groups Diet:Western_907 = 8, Diet:Prudent_611 = 13, Diet:Pooled_Western = 3, Diet:Pooled_Prudent = 3, Diet:Pooled_All = 3"
    if not key_matches(KEYS["D"][0], factors):
        raise SystemExit("factor window match failed")
    if key_matches(KEYS["B"][2], "the count was 1024"):
        raise SystemExit("numeric 102 matched inside 1024")
    if not key_matches(KEYS["B"][2], "102 named metabolites"):
        raise SystemExit("numeric 102 did not match a bare count")
    quoted = _quote_double('alpha "beta" \\" end')
    parsed = parse_pi_args(quoted, honor_backslash=True)
    if parsed != ['alpha "beta" \\" end']:
        raise SystemExit(f"double-quote roundtrip failed: {parsed!r}")
    folded = """```yaml
evaluation: competency-answerability
verdict: present
checks:
  - id: q1
    question: "How many named metabolites does analysis AN000001 report?"
    result: pass
    answer: >
      102
    evidence: "num_metabolites 102"
```
"""
    folded_grade = grade_run("B", folded)
    by_fold = {row["id"]: row for row in folded_grade["questions"]}  # type: ignore[index]
    if not by_fold["MW-6"]["key_match"]:
        raise SystemExit(f"folded numeric answer was not parsed: {by_fold['MW-6']}")
    print("self-test ok")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    prep = sub.add_parser("prepare")
    prep.add_argument("--source", type=Path, required=True)
    prep.add_argument("--out", type=Path, required=True)
    prep.add_argument("--runs", required=True)

    msg = sub.add_parser("message")
    msg.add_argument("--yaml", type=Path, required=True)

    grade = sub.add_parser("grade")
    grade.add_argument("--out", type=Path, required=True)

    test = sub.add_parser("self-test")
    test.add_argument("--repo", type=Path, required=True)

    args = parser.parse_args(argv)
    if args.cmd == "prepare":
        runs = [part.strip().upper() for part in args.runs.split(",") if part.strip()]
        prepare(args.source, args.out, runs)
        return 0
    if args.cmd == "message":
        yaml_text = args.yaml.read_text(encoding="utf-8")
        sys.stdout.write(build_message(ORIGIN, yaml_text) + "\n")
        return 0
    if args.cmd == "grade":
        score = write_grade(args.out)
        print(render_score_md(score))
        return 0
    if args.cmd == "self-test":
        self_test(args.repo)
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
