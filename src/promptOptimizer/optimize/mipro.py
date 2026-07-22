"""MIPROv2: Bayesian search over instructions + demonstrations.

Requires the Optuna extra: ``uv add "dspy[optuna]"`` (already in pyproject).

Always pass an explicit ``valset`` so MIPROv2 does not carve 80% of train into
validation (which starves bootstrapping on small corpora).
"""
from dspy.teleprompt import MIPROv2

from defs.evaluate import run_eval
from defs.metrics import make_metrics
from defs.program import ArtifactGenerator
from optimize import artifact_path

BRANCH = "mipro"


def run(task, trainset, valset, testset, num_threads=8, auto="light", **_):
    scalar, _ = make_metrics(task)
    optimizer = MIPROv2(metric=scalar, auto=auto, num_threads=num_threads)
    compiled = optimizer.compile(
        ArtifactGenerator(task),
        trainset=trainset,
        valset=valset,
        requires_permission_to_run=False,  # run non-interactively
    )
    path = artifact_path(task.name, BRANCH)
    compiled.save(path, save_program=False)
    return run_eval(compiled, testset, scalar, num_threads), path
