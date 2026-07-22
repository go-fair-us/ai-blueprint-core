"""Configurable input/output directories for run isolation.

Defaults match the historical layout: everything under ``<package>/artifacts``.

Resolution (set once at CLI entry via ``configure_paths``)::

    workdir   = --workdir   or <package>/artifacts
    inputdir  = --inputdir  or workdir
    outputdir = --outputdir or workdir

Reads (scenarios, blueprint) prefer ``inputdir``, then ``outputdir`` where noted.
Writes (programs, comparison, report, scenario gen, blueprint cache) go to
``outputdir``.
"""
from __future__ import annotations

import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ARTIFACTS = PACKAGE_ROOT / "artifacts"

# Process-global paths; configure_paths() reassigns these at CLI start.
WORKDIR: Path = DEFAULT_ARTIFACTS
INPUTDIR: Path = DEFAULT_ARTIFACTS
OUTPUTDIR: Path = DEFAULT_ARTIFACTS

# Legacy alias: modules that previously used defs.blueprint.ARTIFACTS for writes
# should use OUTPUTDIR / helpers. ARTIFACTS tracks OUTPUTDIR for compatibility.
ARTIFACTS: Path = DEFAULT_ARTIFACTS

_configured = False


def configure_paths(
    workdir: str | Path | None = None,
    inputdir: str | Path | None = None,
    outputdir: str | Path | None = None,
    *,
    announce: bool = True,
) -> None:
    """Set workdir / inputdir / outputdir for this process.

    Call once from the CLI before any load/save. Defaults preserve historical
    behavior (all paths under ``artifacts/``).
    """
    global WORKDIR, INPUTDIR, OUTPUTDIR, ARTIFACTS, _configured

    wd = Path(workdir).expanduser().resolve() if workdir else DEFAULT_ARTIFACTS
    ind = Path(inputdir).expanduser().resolve() if inputdir else wd
    outd = Path(outputdir).expanduser().resolve() if outputdir else wd

    WORKDIR = wd
    INPUTDIR = ind
    OUTPUTDIR = outd
    ARTIFACTS = outd  # write-side alias
    _configured = True

    if announce and (workdir or inputdir or outputdir):
        print(f"[paths] inputdir={INPUTDIR}", file=sys.stderr)
        print(f"[paths] outputdir={OUTPUTDIR}", file=sys.stderr)


def ensure_output_dir() -> Path:
    """Create outputdir (and parents) if needed; return it."""
    OUTPUTDIR.mkdir(parents=True, exist_ok=True)
    return OUTPUTDIR


def scenarios_filename(task_name: str) -> str:
    return f"scenarios-{task_name}.json"


def scenarios_read_path(task_name: str) -> Path | None:
    """First existing scenarios file: inputdir, then outputdir. None if missing."""
    name = scenarios_filename(task_name)
    for root in (INPUTDIR, OUTPUTDIR):
        p = root / name
        if p.is_file():
            return p
    return None


def scenarios_write_path(task_name: str) -> Path:
    """Where gen-scenarios writes the scenario pack."""
    ensure_output_dir()
    return OUTPUTDIR / scenarios_filename(task_name)


def blueprint_read_path() -> Path | None:
    """First existing blueprint.md: inputdir, then outputdir."""
    for root in (INPUTDIR, OUTPUTDIR):
        p = root / "blueprint.md"
        if p.is_file() and p.stat().st_size > 0:
            return p
    return None


def blueprint_write_path() -> Path:
    """Where a freshly fetched Blueprint cache is stored."""
    ensure_output_dir()
    return OUTPUTDIR / "blueprint.md"


def program_path(task_name: str, branch: str) -> Path:
    ensure_output_dir()
    return OUTPUTDIR / f"{task_name}-{branch}.json"


def comparison_path(task_name: str) -> Path:
    ensure_output_dir()
    return OUTPUTDIR / f"comparison-{task_name}.json"


def report_path(task_name: str) -> Path:
    ensure_output_dir()
    return OUTPUTDIR / f"report-{task_name}.md"


def run_meta_path() -> Path:
    ensure_output_dir()
    return OUTPUTDIR / "run-meta.json"


def run_log_path() -> Path:
    ensure_output_dir()
    return OUTPUTDIR / "run-log.jsonl"


def resolve_program_arg(program: str) -> Path:
    """Resolve ``--program``: as given if it exists, else look under outputdir."""
    p = Path(program).expanduser()
    if p.is_file():
        return p.resolve()
    # Bare name or relative path not found from cwd → try outputdir
    candidate = OUTPUTDIR / p.name
    if candidate.is_file():
        return candidate.resolve()
    # Return original resolved path so callers get a clear missing-file error
    return p if p.is_absolute() else (Path.cwd() / p).resolve()
