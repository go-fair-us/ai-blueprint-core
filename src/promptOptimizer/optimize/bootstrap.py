"""BootstrapFewShot: teacher-generated few-shot demos, filtered by the metric."""
from dspy.teleprompt import BootstrapFewShot

from defs.config import get_active_config
from defs.evaluate import run_eval
from defs.metrics import make_metrics
from defs.program import ArtifactGenerator
from optimize import artifact_path

BRANCH = "bootstrap"


def run(task, trainset, valset, testset, num_threads=8, **_):
    del valset  # BootstrapFewShot has no valset selection step
    scalar, _ = make_metrics(task)

    boot = None
    app = get_active_config()
    if app is not None:
        boot = app.optimizers.bootstrap
    metric_threshold = boot.metric_threshold if boot else 0.7
    max_bootstrapped = boot.max_bootstrapped_demos if boot else 4
    max_labeled = boot.max_labeled_demos if boot else 4

    optimizer = BootstrapFewShot(
        metric=scalar,
        metric_threshold=metric_threshold,
        max_bootstrapped_demos=max_bootstrapped,
        max_labeled_demos=max_labeled,
    )
    compiled = optimizer.compile(ArtifactGenerator(task), trainset=trainset)
    path = artifact_path(task.name, BRANCH)
    compiled.save(path, save_program=False)
    return run_eval(compiled, testset, scalar, num_threads), path
