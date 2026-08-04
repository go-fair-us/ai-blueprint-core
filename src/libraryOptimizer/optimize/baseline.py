"""Baseline: evaluate the un-optimized (seed) program once."""
from defs.evaluate import run_eval
from defs.metric import make_metrics
from defs.program import ArtifactGenerator
from optimize import artifact_path

BRANCH = "baseline"


def run(task, trainset, valset, testset, num_threads=8, **_):
    del trainset, valset
    program = ArtifactGenerator(task)
    scalar, _ = make_metrics(task)
    path = artifact_path(task.name, BRANCH)
    program.save(path, save_program=False)
    return run_eval(program, testset, scalar, num_threads), path, None
