"""GEPA: reflective instruction optimization for one library prompt."""
from __future__ import annotations

import dspy

from defs import paths as pathconf
from defs.evaluate import run_eval
from defs.metric import make_metrics
from defs.program import ArtifactGenerator
from defs.prompts import extract, instructions_text
from optimize import artifact_path

BRANCH = "gepa"


def run(
    task,
    trainset,
    valset,
    testset,
    num_threads=8,
    auto="light",
    reflection_lm=None,
    gepa_budget=None,
    **_,
):
    if reflection_lm is None:
        raise SystemExit("GEPA needs a reflection LM (pass one from main).")
    scalar, feedback = make_metrics(task)
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

    # Human-readable optimized prompt body
    opt_md = pathconf.optimized_prompt_path(task.name)
    text = instructions_text(extract(compiled))
    opt_md.write_text(
        f"# Optimized prompt: {task.name}\n\n"
        f"Source: `{getattr(task, 'source_path', '')}`\n\n"
        f"---\n\n# Prompt\n\n{text}\n",
        encoding="utf-8",
    )

    eval_result = run_eval(compiled, testset, scalar, num_threads)
    return eval_result, path, str(opt_md)
