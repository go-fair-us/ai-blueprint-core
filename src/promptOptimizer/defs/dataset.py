"""Scenario data, per task: load curated scenarios, or fall back to config seeds.

Scoring is reference-free, so examples carry only the input field (usually
``task_description``). Curate a real set with ``main.py gen-scenarios --task <t>``
(writes ``scenarios-<t>.json`` under the configured outputdir).

Data is split three ways so optimizers never see the final test scores:

* **train** — bootstrapping demos / reflective updates
* **val**   — candidate selection inside GEPA / MIPROv2 (not final report)
* **test**  — held-out final evaluation only (``compare`` / ``eval``)

Split fractions come from ``config/default.yaml`` ``data:`` when an AppConfig
is active.
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

import dspy

from defs import paths as pathconf
from defs.config import get_active_config
from tasks.base import BrainstormScenarios


def scenarios_path(task_name: str):
    """Preferred path for reading scenarios (inputdir, else outputdir write path)."""
    found = pathconf.scenarios_read_path(task_name)
    if found is not None:
        return found
    return pathconf.scenarios_write_path(task_name)


def _try_load_json_scenarios(path: Path) -> list[str] | None:
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    scenarios = data.get("scenarios", data) if isinstance(data, dict) else data
    if scenarios:
        return list(scenarios)
    return None


def load_scenarios(task) -> list[str]:
    """Load scenarios: inputdir/outputdir JSON, optional task.scenarios_file, then seeds."""
    # 1) Standard package layout: scenarios-<task>.json
    path = pathconf.scenarios_read_path(task.name)
    if path is not None:
        loaded = _try_load_json_scenarios(path)
        if loaded:
            return loaded

    # 2) Task config may name a file (relative to inputdir, outputdir, or absolute)
    sc_file = getattr(task, "scenarios_file", None)
    if sc_file:
        candidates = [
            Path(sc_file),
            pathconf.INPUTDIR / sc_file,
            pathconf.OUTPUTDIR / sc_file,
        ]
        app = get_active_config()
        if app is not None:
            candidates.append(app.root / sc_file)
        for c in candidates:
            if c.is_file():
                loaded = _try_load_json_scenarios(c.resolve())
                if loaded:
                    return loaded

    return list(task.seed_scenarios)


def build_examples(
    task,
    seed: int = 0,
    train_frac: float | None = None,
    val_frac: float | None = None,
    min_val: int | None = None,
    min_test: int | None = None,
):
    """Return ``(trainset, valset, testset)`` as shuffled dspy.Examples.

    Fractions default from active AppConfig ``data:`` section, else 0.5 / 0.25
    with min_val/min_test floors of 3.
    """
    app = get_active_config()
    if app is not None:
        train_frac = app.data.train_frac if train_frac is None else train_frac
        val_frac = app.data.val_frac if val_frac is None else val_frac
        min_val = app.data.min_val if min_val is None else min_val
        min_test = app.data.min_test if min_test is None else min_test
    else:
        train_frac = 0.5 if train_frac is None else train_frac
        val_frac = 0.25 if val_frac is None else val_frac
        min_val = 3 if min_val is None else min_val
        min_test = 3 if min_test is None else min_test

    input_field = getattr(task, "input_field", "task_description")
    examples = [
        dspy.Example(**{input_field: s}).with_inputs(input_field)
        for s in load_scenarios(task)
    ]
    random.Random(seed).shuffle(examples)
    n = len(examples)

    if n < 3:
        print(
            f"[data] only {n} scenario(s) — using the same examples for train/val/test. "
            f"Run 'gen-scenarios --task {task.name} --n 40' before trusting scores.",
            file=sys.stderr,
        )
        return examples, list(examples), list(examples)

    n_test = max(min_test, int(round(n * (1.0 - train_frac - val_frac))))
    n_val = max(min_val, int(round(n * val_frac)))
    max_holdout = max(0, n - max(1, int(n * 0.4)))
    while n_test + n_val > max_holdout and (n_test > 1 or n_val > 1):
        if n_test >= n_val and n_test > 1:
            n_test -= 1
        elif n_val > 1:
            n_val -= 1
        else:
            break
    n_train = n - n_val - n_test
    if n_train < 1:
        n_train = 1
        n_val = max(1, (n - 1) // 2)
        n_test = n - n_train - n_val

    trainset = examples[:n_train]
    valset = examples[n_train : n_train + n_val]
    testset = examples[n_train + n_val :]

    if not valset:
        valset = trainset[-1:]
    if not testset:
        testset = valset[-1:]

    if n < 20 or len(valset) < min_val or len(testset) < min_test:
        print(
            f"[data] small dataset: {n} scenarios -> {len(trainset)} train / "
            f"{len(valset)} val / {len(testset)} test. Scores will be noisy; run "
            f"'gen-scenarios --task {task.name} --n 40' for a more reliable comparison.",
            file=sys.stderr,
        )
    return trainset, valset, testset


def generate_scenarios(task, n: int = 40) -> list[str]:
    """Use the configured LM to brainstorm scenarios for a task; writes to outputdir."""
    out = dspy.ChainOfThought(BrainstormScenarios)(domain_context=task.domain_context, n=n)
    seen, unique = set(), []
    for s in (out.scenarios or []):
        s = s.strip()
        if s and s.lower() not in seen:
            seen.add(s.lower())
            unique.append(s)
    path = pathconf.scenarios_write_path(task.name)
    path.write_text(json.dumps({"scenarios": unique}, indent=2), encoding="utf-8")
    if pathconf.INPUTDIR != pathconf.OUTPUTDIR:
        print(
            f"[data] scenarios written to {path}. "
            f"Optimize runs read inputdir first ({pathconf.INPUTDIR}); "
            f"copy the file there or pass --inputdir/--workdir pointing at this output.",
            file=sys.stderr,
        )
    return unique
