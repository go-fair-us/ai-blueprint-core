"""Build Pi prompt templates from prompts/evals and check the committed copies.

The procedure text stays in prompts/evals. extensions/prompts holds the Pi
template: frontmatter, bound arguments, then that same procedure. This module
is the rule for that wrapper. ./bin/pi only reads the committed templates.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EVALS_DIR = REPO_ROOT / "prompts" / "evals"
PROMPTS_DIR = REPO_ROOT / "extensions" / "prompts"

DEFAULT_HINT = "<origin-url> [record-url]"
DEFAULT_BINDINGS = (
    "Repository origin: $1",
    "Record URL: ${2:-none}",
)

# Files whose second or third argument is not a record URL.
SHAPES: dict[str, tuple[str, tuple[str, ...]]] = {
    "openapi-discovery": (
        "<origin-url> [spec-url]",
        (
            "Repository origin: $1",
            "Spec URL: ${2:-none}",
        ),
    ),
    "metadata-api": (
        "<origin-url> [record-url] [metadata-url]",
        (
            "Repository origin: $1",
            "Record URL: ${2:-none}",
            "Metadata URL: ${3:-none}",
        ),
    ),
    "api-http-behavior": (
        "<origin-url> [metadata-url] [record-url]",
        (
            "Repository origin: $1",
            "Metadata URL: ${2:-none}",
            "Record URL: ${3:-none}",
        ),
    ),
    "competency-answerability": (
        "<origin-url> [questions]",
        (
            "Repository origin: $1",
            "Questions: ${2:-none}",
        ),
    ),
}

HEADER_NOTE = """The values above are the inputs for this run. When a value is `none`, follow the procedure's rule for that missing input. If the origin is empty, stop and ask for the repository origin URL. Do not fetch.

Follow the evaluation below exactly. Stay inside its checks.
"""


def question_line(procedure: str, name: str) -> str:
    prefix = "**Question:** "
    for line in procedure.splitlines():
        if line.startswith(prefix):
            question = line[len(prefix) :].strip()
            if question:
                return question
    raise ValueError(f"{name} has no **Question:** line")


def render_template(name: str, procedure: str) -> str:
    hint, bindings = SHAPES.get(name, (DEFAULT_HINT, DEFAULT_BINDINGS))
    description = json.dumps(question_line(procedure, name), ensure_ascii=False)
    argument_hint = json.dumps(hint, ensure_ascii=False)
    body = procedure if procedure.endswith("\n") else procedure + "\n"
    binding_block = "\n".join(bindings)
    return (
        "---\n"
        f"description: {description}\n"
        f"argument-hint: {argument_hint}\n"
        "---\n"
        "\n"
        f"{binding_block}\n"
        "\n"
        f"{HEADER_NOTE}\n"
        f"{body}"
    )


def eval_procedures() -> dict[str, str]:
    files = sorted(EVALS_DIR.glob("*.md"))
    if not files:
        raise ValueError(f"no eval files in {EVALS_DIR}")
    return {path.stem: path.read_text(encoding="utf-8") for path in files}


def expected_templates() -> dict[str, str]:
    return {name: render_template(name, text) for name, text in eval_procedures().items()}


def committed_templates() -> dict[str, str]:
    files = sorted(PROMPTS_DIR.glob("*.md"))
    return {path.stem: path.read_text(encoding="utf-8") for path in files}


def drift() -> list[str]:
    expected = expected_templates()
    committed = committed_templates()
    problems: list[str] = []
    for name in sorted(set(expected) | set(committed)):
        if name not in expected:
            problems.append(f"extra template: extensions/prompts/{name}.md")
        elif name not in committed:
            problems.append(f"missing template: extensions/prompts/{name}.md")
        elif committed[name] != expected[name]:
            problems.append(f"template drifted from prompts/evals/{name}.md")
    return problems


def write_templates() -> None:
    PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
    expected = expected_templates()
    for name, text in expected.items():
        (PROMPTS_DIR / f"{name}.md").write_text(text, encoding="utf-8")
    for path in PROMPTS_DIR.glob("*.md"):
        if path.stem not in expected:
            path.unlink()


if __name__ == "__main__":
    import sys

    if "--write" in sys.argv:
        write_templates()
        print(f"wrote {len(expected_templates())} templates to {PROMPTS_DIR}")
    else:
        problems = drift()
        if problems:
            print("\n".join(problems), file=sys.stderr)
            sys.exit(1)
        print(f"{len(expected_templates())} templates match prompts/evals")
