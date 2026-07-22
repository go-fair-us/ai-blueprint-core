"""Optimizer branches. Each module exposes ``run(task, ...)`` returning
``(eval_result, artifact_path)``.

The branches are alternatives, not a pipeline: every one compiles from the same
un-optimized ``ArtifactGenerator(task)``, uses train/val for optimization, and is
scored on the same held-out **test** set through the same evaluation harness, so
their results are comparable. Compiled programs are saved per task and branch
(``<outputdir>/<task>-<branch>.json``).
"""


from defs import paths as pathconf


def artifact_path(task_name: str, branch: str) -> str:
    """Absolute path under the configured outputdir."""
    return str(pathconf.program_path(task_name, branch))
