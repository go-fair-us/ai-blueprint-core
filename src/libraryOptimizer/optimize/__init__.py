"""Optimizer branches for libraryOptimizer (GEPA + optional baseline)."""

from defs import paths as pathconf


def artifact_path(task_name: str, branch: str) -> str:
    """Absolute path under the configured outputdir."""
    return str(pathconf.program_path(task_name, branch))
