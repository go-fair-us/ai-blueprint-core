"""Read-only access to the niaid-bp-* Agent Skill bundle.

Exposes a catalog (frontmatter), progressive file reads, and a SHACL wrapper
around ``niaid-bp-validation/scripts/validate.py``. Interview procedures stay
in ``SKILL.md`` — this module does not re-encode them as one tool per step.
"""

from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path
from typing import Any

import yaml

from .config import SKILLS_DIR
from .content import ContentError

SKILL_FILENAME = "SKILL.md"

# Files a client may pull when deepening a skill (references, assets, scripts).
ALLOWED_SKILL_EXTENSIONS: tuple[str, ...] = (
    ".md",
    ".json",
    ".jsonld",
    ".ttl",
    ".txt",
    ".html",
    ".css",
    ".srl",
    ".py",
    ".ts",
    ".sh",
    ".yaml",
    ".yml",
)

_GRAPH_SUFFIX: dict[str, str] = {
    "json-ld": ".jsonld",
    "jsonld": ".jsonld",
    "json": ".jsonld",
    "turtle": ".ttl",
    "ttl": ".ttl",
}


class SkillsError(ContentError):
    """Raised when a skill cannot be located or a path is invalid."""


def _skills_root() -> Path:
    return SKILLS_DIR.resolve()


def _parse_frontmatter(text: str) -> dict[str, Any]:
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    try:
        data = yaml.safe_load(parts[1])
    except yaml.YAMLError:
        return {}
    return data if isinstance(data, dict) else {}


def _skill_dir(name: str) -> Path:
    if not name or name in {".", ".."} or "/" in name or "\\" in name:
        raise SkillsError(f"Invalid skill name: {name!r}")
    root = _skills_root()
    candidate = (root / name).resolve()
    if root != candidate.parent:
        raise SkillsError(f"Invalid skill name: {name!r}")
    skill_md = candidate / SKILL_FILENAME
    if not skill_md.is_file():
        raise SkillsError(f"Unknown skill: {name!r}")
    return candidate


def _has_nonempty_dir(path: Path) -> bool:
    if not path.is_dir():
        return False
    return any(child.is_file() or child.is_dir() for child in path.iterdir())


def _entry_from_dir(skill_dir: Path) -> dict[str, object]:
    text = (skill_dir / SKILL_FILENAME).read_text(encoding="utf-8", errors="replace")
    meta = _parse_frontmatter(text)
    name = str(meta.get("name") or skill_dir.name)
    description = meta.get("description")
    if isinstance(description, str):
        description = " ".join(description.split())
    else:
        description = ""
    when_to_use = meta.get("when_to_use")
    if isinstance(when_to_use, str):
        when_to_use = " ".join(when_to_use.split())
    else:
        when_to_use = None
    return {
        "name": name,
        "directory": skill_dir.name,
        "description": description,
        "when_to_use": when_to_use,
        "license": meta.get("license"),
        "has_scripts": _has_nonempty_dir(skill_dir / "scripts"),
        "has_references": _has_nonempty_dir(skill_dir / "references"),
        "has_assets": _has_nonempty_dir(skill_dir / "assets"),
    }


def list_skills() -> list[dict[str, object]]:
    """List skill directories that contain a ``SKILL.md``."""

    root = _skills_root()
    if not root.is_dir():
        return []
    entries: list[dict[str, object]] = []
    for child in sorted(root.iterdir(), key=lambda p: p.name):
        if child.is_dir() and (child / SKILL_FILENAME).is_file():
            entries.append(_entry_from_dir(child))
    return entries


def read_skill(name: str) -> str:
    """Return the full ``SKILL.md`` text for ``name``."""

    path = _skill_dir(name) / SKILL_FILENAME
    return path.read_text(encoding="utf-8", errors="replace")


def read_skill_file(name: str, relpath: str) -> dict[str, object]:
    """Read one file under a skill directory (path-traversal safe)."""

    if not relpath or relpath.startswith("/") or relpath.startswith("\\"):
        raise SkillsError(f"Invalid skill file path: {relpath!r}")

    skill_dir = _skill_dir(name)
    candidate = (skill_dir / relpath).resolve()
    if skill_dir != candidate and skill_dir not in candidate.parents:
        raise SkillsError(f"Path escapes the skill directory: {relpath!r}")
    if candidate.suffix.lower() not in ALLOWED_SKILL_EXTENSIONS:
        allowed = ", ".join(ALLOWED_SKILL_EXTENSIONS)
        raise SkillsError(
            f"Only these extensions are served: {allowed} (got {candidate.suffix!r})"
        )
    if not candidate.is_file():
        raise SkillsError(f"File not found: {relpath!r}")

    text = candidate.read_text(encoding="utf-8", errors="replace")
    return {
        "skill": name,
        "path": candidate.relative_to(skill_dir).as_posix(),
        "bytes": len(text.encode("utf-8")),
        "text": text,
    }


def _load_validate_module():
    script = _skills_root() / "niaid-bp-validation" / "scripts" / "validate.py"
    if not script.is_file():
        raise SkillsError(
            "niaid-bp-validation/scripts/validate.py not found under BLUEPRINT_SKILLS_DIR."
        )
    spec = importlib.util.spec_from_file_location("niaid_bp_validate", script)
    if spec is None or spec.loader is None:
        raise SkillsError("Could not load niaid-bp-validation/scripts/validate.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_dataset(
    graph: str,
    data_format: str | None = None,
) -> dict[str, object]:
    """Run the bundled Blueprint SHACL shape against a Dataset graph string."""

    if not graph or not graph.strip():
        raise SkillsError("graph is empty.")

    fmt = (data_format or "json-ld").strip().lower()
    suffix = _GRAPH_SUFFIX.get(fmt)
    if suffix is None:
        raise SkillsError(
            f"Unsupported data_format {data_format!r}. Use json-ld or turtle."
        )

    try:
        validate_mod = _load_validate_module()
    except SkillsError:
        raise
    except ImportError as exc:
        raise SkillsError(
            "pyshacl and rdflib are required for validate_dataset. "
            "Install with: uv sync --extra validation"
        ) from exc

    with tempfile.TemporaryDirectory(prefix="mcp_bp_validate_") as tmp:
        tmp_path = Path(tmp)
        data_path = tmp_path / f"dataset{suffix}"
        data_path.write_text(graph, encoding="utf-8")
        try:
            summary = validate_mod.run_validation(
                data_path,
                out_dir=tmp_path / "out",
            )
        except FileNotFoundError as exc:
            raise SkillsError(str(exc)) from exc
        except RuntimeError as exc:
            raise SkillsError(str(exc)) from exc

    return {
        "conforms": bool(summary.get("conforms")),
        "raw_conforms": bool(summary.get("raw_conforms")),
        "n_violations": summary.get("n_violations", 0),
        "n_warnings": summary.get("n_warnings", 0),
        "n_info": summary.get("n_info", 0),
        "data_format": summary.get("data_format"),
        "shape": "niaid-bp-validation/assets/blueprint-required.ttl",
        "results": summary.get("results") or [],
    }


def skills_stats() -> dict[str, object]:
    entries = list_skills()
    return {
        "count": len(entries),
        "names": [e["name"] for e in entries],
        "root_exists": _skills_root().is_dir(),
    }
