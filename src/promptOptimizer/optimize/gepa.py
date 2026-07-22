"""GEPA: reflective / evolutionary instruction optimization.

Uses the task's feedback metric (score + textual feedback) to compile, the
task's scalar metric to evaluate, and a strong reflection LM supplied by
``main``. An explicit ``valset`` drives Pareto candidate selection; the held-out
``testset`` is used only for the final report score.
"""
import dspy

from defs.evaluate import run_eval
from defs.metrics import make_metrics
from defs.program import ArtifactGenerator
from optimize import artifact_path

BRANCH = "gepa"


def run(task, trainset, valset, testset, num_threads=8, auto="light", reflection_lm=None,
        gepa_budget=None, **_):
    if reflection_lm is None:
        raise SystemExit("GEPA needs a reflection LM (pass one from main).")
    scalar, feedback = make_metrics(task)
    # --gepa-budget caps total metric evaluations (rollouts); otherwise use the
    # auto preset (which can be hundreds of rollouts — slow on a slow endpoint).
    common = dict(
        metric=feedback,
        reflection_lm=reflection_lm,
        num_threads=num_threads,
    )
    if gepa_budget:
        optimizer = dspy.GEPA(**common, max_metric_calls=int(gepa_budget))
    else:
        optimizer = dspy.GEPA(**common, auto=auto)
    compiled = optimizer.compile(
        ArtifactGenerator(task),
        trainset=trainset,
        valset=valset,
    )
    path = artifact_path(task.name, BRANCH)
    compiled.save(path, save_program=False)
    return run_eval(compiled, testset, scalar, num_threads), path
