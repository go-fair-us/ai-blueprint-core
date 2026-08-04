"""Scenario load/generate and train/val/test split."""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

import dspy

from defs import paths as pathconf
from defs.config import get_active_config
from defs.metric import BrainstormScenarios


def load_scenarios(task) -> list[str]:
    path = pathconf.scenarios_read_path(task.name)
    if path is not None:
        data = json.loads(path.read_text(encoding="utf-8"))
        scenarios = data.get("scenarios", data) if isinstance(data, dict) else data
        if scenarios:
            return list(scenarios)
    return list(task.seed_scenarios)


def build_examples(
    task,
    seed: int = 0,
    train_frac: float | None = None,
    val_frac: float | None = None,
    min_val: int | None = None,
    min_test: int | None = None,
):
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

    input_field = getattr(task, "input_field", "scenario")
    examples = [
        dspy.Example(**{input_field: s}).with_inputs(input_field)
        for s in load_scenarios(task)
    ]
    random.Random(seed).shuffle(examples)
    n = len(examples)

    if n < 3:
        print(
            f"[data] only {n} scenario(s) — using the same examples for train/val/test. "
            f"Run 'gen-scenarios --prompt … --n 20' before trusting scores.",
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
            f"{len(valset)} val / {len(testset)} test.",
            file=sys.stderr,
        )
    return trainset, valset, testset


def generate_scenarios(task, n: int = 20) -> list[str]:
    """Brainstorm scenarios with the configured task LM; write JSON pack."""
    out = dspy.ChainOfThought(BrainstormScenarios)(
        domain_context=task.domain_context, n=n
    )
    seen: set[str] = set()
    unique: list[str] = []
    for s in out.scenarios or []:
        s = str(s).strip()
        if s and s.lower() not in seen:
            seen.add(s.lower())
            unique.append(s)
    path = pathconf.scenarios_write_path(task.name)
    path.write_text(json.dumps({"scenarios": unique}, indent=2), encoding="utf-8")
    return unique


def ensure_scenarios(task, n: int | None = None) -> list[str]:
    """Load scenarios or auto-generate if missing."""
    existing = pathconf.scenarios_read_path(task.name)
    if existing is not None:
        return load_scenarios(task)
    app = get_active_config()
    count = n if n is not None else (app.data.n_scenarios if app else 20)
    print(
        f"[data] no scenarios for {task.name!r}; generating {count}…",
        file=sys.stderr,
    )
    return generate_scenarios(task, n=count)
