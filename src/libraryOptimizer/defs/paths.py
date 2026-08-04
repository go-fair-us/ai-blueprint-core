"""Configurable input/output directories for run isolation.

Defaults: everything under ``<package>/artifacts``.

    workdir   = --workdir   or <package>/artifacts
    inputdir  = --inputdir  or workdir
    outputdir = --outputdir or workdir
"""
from __future__ import annotations

import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
# src/libraryOptimizer → src → repo root
REPO_ROOT = PACKAGE_ROOT.parent.parent
DEFAULT_ARTIFACTS = PACKAGE_ROOT / "artifacts"

WORKDIR: Path = DEFAULT_ARTIFACTS
INPUTDIR: Path = DEFAULT_ARTIFACTS
OUTPUTDIR: Path = DEFAULT_ARTIFACTS
ARTIFACTS: Path = DEFAULT_ARTIFACTS

_configured = False


def configure_paths(
    workdir: str | Path | None = None,
    inputdir: str | Path | None = None,
    outputdir: str | Path | None = None,
    *,
    announce: bool = True,
) -> None:
    """Set workdir / inputdir / outputdir for this process."""
    global WORKDIR, INPUTDIR, OUTPUTDIR, ARTIFACTS, _configured

    wd = Path(workdir).expanduser().resolve() if workdir else DEFAULT_ARTIFACTS
    ind = Path(inputdir).expanduser().resolve() if inputdir else wd
    outd = Path(outputdir).expanduser().resolve() if outputdir else wd

    WORKDIR = wd
    INPUTDIR = ind
    OUTPUTDIR = outd
    ARTIFACTS = outd
    _configured = True

    if announce and (workdir or inputdir or outputdir):
        print(f"[paths] inputdir={INPUTDIR}", file=sys.stderr)
        print(f"[paths] outputdir={OUTPUTDIR}", file=sys.stderr)


def ensure_output_dir() -> Path:
    OUTPUTDIR.mkdir(parents=True, exist_ok=True)
    return OUTPUTDIR


def scenarios_filename(slug: str) -> str:
    return f"scenarios-{slug}.json"


def scenarios_read_path(slug: str) -> Path | None:
    name = scenarios_filename(slug)
    for root in (INPUTDIR, OUTPUTDIR):
        p = root / name
        if p.is_file():
            return p
    return None


def scenarios_write_path(slug: str) -> Path:
    ensure_output_dir()
    return OUTPUTDIR / scenarios_filename(slug)


def guidance_write_path() -> Path:
    ensure_output_dir()
    return OUTPUTDIR / "guidance.md"


def program_path(slug: str, branch: str) -> Path:
    ensure_output_dir()
    return OUTPUTDIR / f"{slug}-{branch}.json"


def optimized_prompt_path(slug: str) -> Path:
    ensure_output_dir()
    return OUTPUTDIR / f"{slug}-optimized-prompt.md"


def report_path(slug: str) -> Path:
    ensure_output_dir()
    return OUTPUTDIR / f"report-{slug}.md"


def resolve_program_arg(program: str) -> Path:
    p = Path(program).expanduser()
    if p.is_file():
        return p.resolve()
    candidate = OUTPUTDIR / p.name
    if candidate.is_file():
        return candidate.resolve()
    return p if p.is_absolute() else (Path.cwd() / p).resolve()


def resolve_repo_path(rel: str | Path) -> Path:
    """Resolve a path relative to repo root, or absolute as-is."""
    p = Path(rel).expanduser()
    if p.is_absolute():
        return p
    return (REPO_ROOT / p).resolve()
