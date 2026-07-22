"""CLI entry point for the Blueprint prompt optimizer.

One optimizer harness + one **active profile** (goal) per run. Models and run
knobs live in ``config/default.yaml``; the goal (seed, rubric, weights,
scenarios) lives in ``config/profile.yaml`` or a library recipe under
``config/profiles/``. Different goals = different runs (``--profile`` /
``--workdir``), not a multi-task product switch.

    uv run main.py gen-scenarios --n 40
    uv run main.py baseline
    uv run main.py gepa --gepa-budget 60
    uv run main.py compare

    # Metadata-focused run (separate workdir recommended)
    uv run main.py compare --profile metadata --workdir runs/meta-1

    # Or copy a recipe into profile.yaml and run as usual
    #   cp config/profiles/metadata.yaml config/profile.yaml

Shared flags: --config, --profile, --backend, --task-model, --reflection-backend,
--reflection-model, --seed, --num-threads, --auto, --judge, --workdir,
--inputdir, --outputdir.
"""
from __future__ import annotations

import argparse
import json
import sys
import time

import dspy

from defs import paths as pathconf
from defs.config import (
    announce_config,
    get_active_config,
    load_app_config,
    load_profile_config,
    set_active_config,
)
from defs.dataset import build_examples, generate_scenarios, load_scenarios
from defs.evaluate import RunResult, run_eval
from defs.usage import collect_usage, reset_history
from defs.lm import (
    BACKENDS,
    get_reflection_lm,
    get_task_lm,
    refresh_backends,
    resolved_model_ids,
)
from defs.metrics import make_metrics
from defs.program import ArtifactGenerator
from defs.prompts import optimized_prompt, seed_prompt
from defs.provenance import (
    announce_provenance,
    build_entry,
    data_snapshot,
    record_from_run_result,
    record_run,
)
from defs.report import write_report
from optimize import baseline, bootstrap, gepa, mipro
from tasks import clear_task_cache, get_task, set_active_profile
from tasks.base import set_judge_lm

OPTIMIZERS = {"baseline": baseline, "bootstrap": bootstrap, "mipro": mipro, "gepa": gepa}


def _score_of(result) -> float:
    """Normalize dspy.Evaluate's percentage (0–100) to a 0–1 mean metric score."""
    return float(getattr(result, "score", result)) / 100.0


def _early_flag(argv: list[str] | None, name: str) -> str | None:
    """Pull --name VALUE or --name=VALUE from argv before full parse."""
    argv = list(sys.argv[1:] if argv is None else argv)
    flag = f"--{name}"
    for i, a in enumerate(argv):
        if a == flag and i + 1 < len(argv):
            return argv[i + 1]
        if a.startswith(f"{flag}="):
            return a.split("=", 1)[1]
    return None


def _load_and_activate(config_path: str | None, profile_arg: str | None):
    app = load_app_config(config_path)
    set_active_config(app)
    clear_task_cache()
    refresh_backends(app)
    pc = load_profile_config(profile_arg, app)
    set_active_profile(pc)
    announce_config(app, pc)
    return app, pc


def _configure_paths(args) -> None:
    pathconf.configure_paths(
        workdir=getattr(args, "workdir", None),
        inputdir=getattr(args, "inputdir", None),
        outputdir=getattr(args, "outputdir", None),
    )


def _configure(args, app, *, need_judge: bool = True) -> None:
    _configure_paths(args)
    dspy.configure_cache(enable_disk_cache=False, enable_memory_cache=False)
    dspy.configure(
        lm=get_task_lm(args.backend, model=getattr(args, "task_model", None), cfg=app)
    )
    if not need_judge:
        set_judge_lm(None)
    elif getattr(args, "judge", "reflection") == "reflection":
        set_judge_lm(
            get_reflection_lm(
                args.reflection_backend,
                model=args.reflection_model,
                cfg=app,
            )
        )
    else:
        set_judge_lm(None)


def _lms_in_play(reflection_lm=None):
    from tasks.base import JUDGE_LM
    return [dspy.settings.lm, JUDGE_LM, reflection_lm]


def _run_one(name, args, task, trainset, valset, testset, reflection_lm=None) -> RunResult:
    mod = OPTIMIZERS[name]
    lms = _lms_in_play(reflection_lm)
    reset_history(lms)
    start = time.perf_counter()
    result, path = mod.run(
        task=task,
        trainset=trainset,
        valset=valset,
        testset=testset,
        num_threads=args.num_threads,
        auto=args.auto,
        reflection_lm=reflection_lm,
        gepa_budget=getattr(args, "gepa_budget", None),
    )
    seconds = time.perf_counter() - start
    totals, cost, by_model = collect_usage(lms)
    return RunResult(
        name=name,
        score=_score_of(result),
        seconds=seconds,
        artifact=path,
        total_tokens=totals["total_tokens"],
        prompt_tokens=totals["prompt_tokens"],
        completion_tokens=totals["completion_tokens"],
        cost=cost,
        usage_by_lm=by_model,
    )


def _split_info(task, trainset, valset, testset) -> dict:
    n_scen = len(load_scenarios(task))
    return dict(
        n_scenarios=n_scen,
        n_train=len(trainset),
        n_val=len(valset),
        n_test=len(testset),
    )


def cmd_gen_scenarios(args, app) -> None:
    task = get_task()
    _configure(args, app, need_judge=False)
    scenarios = generate_scenarios(task, args.n)
    out = pathconf.scenarios_write_path(task.name)
    print(f"Wrote {len(scenarios)} scenarios to {out}\n")
    for i, s in enumerate(scenarios, 1):
        print(f"{i:2d}. {s}")
    meta_p, log_p = record_run(build_entry(
        command="gen-scenarios",
        args=args,
        task_name=task.name,
        data=data_snapshot(
            task.name,
            n_scenarios=len(scenarios),
            scenarios_source="generated",
        ),
        result={"n_written": len(scenarios), "path": str(out)},
    ))
    announce_provenance(meta_p, log_p)


def cmd_single(args, app) -> None:
    task = get_task()
    _configure(args, app)
    trainset, valset, testset = build_examples(task, seed=args.seed)
    reflection_lm = (
        get_reflection_lm(args.reflection_backend, args.reflection_model, cfg=app)
        if args.command == "gepa" else None
    )
    rr = _run_one(args.command, args, task, trainset, valset, testset, reflection_lm)
    models = resolved_model_ids(
        task_backend=args.backend,
        reflection_backend=args.reflection_backend,
        task_model=getattr(args, "task_model", None),
        reflection_model=args.reflection_model,
        cfg=app,
    )
    print(
        f"\n[{task.name}] {rr.name}: score={rr.score:.3f}  tokens={rr.total_tokens:,} "
        f"(prompt {rr.prompt_tokens:,} / completion {rr.completion_tokens:,})  "
        f"cost=${rr.cost:.4f}  ({rr.seconds:.0f}s)  -> {rr.artifact}"
    )
    print(
        f"  models: task={models['task_model']}  reflection={models['reflection_model']}",
        file=sys.stderr,
    )
    meta_p, log_p = record_from_run_result(
        args, task.name, rr, **_split_info(task, trainset, valset, testset),
    )
    announce_provenance(meta_p, log_p)


def cmd_compare(args, app) -> None:
    task = get_task()
    _configure(args, app)
    trainset, valset, testset = build_examples(task, seed=args.seed)
    reflection_lm = get_reflection_lm(
        args.reflection_backend, args.reflection_model, cfg=app
    )
    rows: list[RunResult] = []
    for name in ("baseline", "bootstrap", "mipro", "gepa"):
        try:
            rl = reflection_lm if name == "gepa" else None
            rr = _run_one(name, args, task, trainset, valset, testset, rl)
            rows.append(rr)
            record_from_run_result(
                args, task.name, rr,
                command=name,
                **_split_info(task, trainset, valset, testset),
            )
        except Exception as e:
            print(f"[{name}] failed: {e}")
            split = _split_info(task, trainset, valset, testset)
            record_run(build_entry(
                command=name,
                args=args,
                task_name=task.name,
                data=data_snapshot(
                    task.name,
                    n_scenarios=split["n_scenarios"],
                    n_train=split["n_train"],
                    n_val=split["n_val"],
                    n_test=split["n_test"],
                ),
                result={"failed": True, "error": str(e)},
            ))
    rows.sort(key=lambda r: r.score, reverse=True)
    print(
        f"\n=== Comparison — profile '{task.name}' "
        f"(higher score is better; tokens/cost = compile + eval) ==="
    )
    print(f"{'optimizer':<12}{'score':>9}{'tokens':>13}{'cost($)':>10}{'seconds':>10}")
    for r in rows:
        print(f"{r.name:<12}{r.score:>9.3f}{r.total_tokens:>13,}{r.cost:>10.4f}{r.seconds:>10.0f}")
    out = pathconf.comparison_path(task.name)
    with open(out, "w") as f:
        json.dump([r.__dict__ for r in rows], f, indent=2)
    print(f"\nSaved {out}")
    report = write_report(task, rows=[r.__dict__ for r in rows])
    print(f"Saved {report}")
    split = _split_info(task, trainset, valset, testset)
    meta_p, log_p = record_run(build_entry(
        command="compare",
        args=args,
        task_name=task.name,
        data=data_snapshot(
            task.name,
            n_scenarios=split["n_scenarios"],
            n_train=split["n_train"],
            n_val=split["n_val"],
            n_test=split["n_test"],
        ),
        result={
            "comparison": str(out),
            "report": report,
            "ranking": [
                {"name": r.name, "score": r.score, "artifact": r.artifact}
                for r in rows
            ],
        },
    ))
    announce_provenance(meta_p, log_p)


def cmd_show_prompt(args, app) -> None:
    del app
    _configure_paths(args)
    task = get_task()
    seed = seed_prompt(task)
    print(f"=== SEED prompt — profile '{task.name}' ===\n")
    print((seed[0]["instructions"].strip() if seed else "(none)"))
    if args.program:
        prog = pathconf.resolve_program_arg(args.program)
        opt = optimized_prompt(task, str(prog))
        instr = opt[0]["instructions"].strip() if opt else "(none)"
        ndemos = len(opt[0]["demos"]) if opt else 0
        print(f"\n=== OPTIMIZED prompt — {prog} ===\n")
        print(instr)
        print(f"\n[few-shot demos: {ndemos}]")
        record_run(build_entry(
            command="show-prompt",
            args=args,
            task_name=task.name,
            result={"program": str(prog), "n_demos": ndemos, "instruction_chars": len(instr)},
        ))


def cmd_report(args, app) -> None:
    del app
    _configure_paths(args)
    task = get_task()
    path = write_report(task)
    print(f"Wrote {path}")
    meta_p, log_p = record_run(build_entry(
        command="report",
        args=args,
        task_name=task.name,
        result={"report": path},
    ))
    announce_provenance(meta_p, log_p)


def cmd_eval(args, app) -> None:
    task = get_task()
    _configure(args, app)
    trainset, valset, testset = build_examples(task, seed=args.seed)
    program = ArtifactGenerator(task)
    prog = pathconf.resolve_program_arg(args.program)
    program.load(str(prog))
    scalar, _ = make_metrics(task)
    lms = _lms_in_play()
    reset_history(lms)
    start = time.perf_counter()
    result = run_eval(program, testset, scalar, args.num_threads)
    seconds = time.perf_counter() - start
    totals, cost, by_model = collect_usage(lms)
    score = _score_of(result)
    print(f"\n{prog}: score={score:.3f}  tokens={totals['total_tokens']:,}  cost=${cost:.4f}")
    split = _split_info(task, trainset, valset, testset)
    meta_p, log_p = record_run(build_entry(
        command="eval",
        args=args,
        task_name=task.name,
        data=data_snapshot(
            task.name,
            n_scenarios=split["n_scenarios"],
            n_train=split["n_train"],
            n_val=split["n_val"],
            n_test=split["n_test"],
        ),
        result={
            "program": str(prog),
            "score": score,
            "seconds": seconds,
            "total_tokens": totals["total_tokens"],
            "prompt_tokens": totals["prompt_tokens"],
            "completion_tokens": totals["completion_tokens"],
            "cost": cost,
            "usage_by_lm": by_model,
        },
    ))
    announce_provenance(meta_p, log_p)


def _add_common(p: argparse.ArgumentParser, app) -> None:
    backends = list(app.backend_names()) or list(BACKENDS)
    p.add_argument(
        "--config",
        default=None,
        help="Config file or directory (default: package config/ or PROMPT_OPTIMIZER_CONFIG).",
    )
    p.add_argument(
        "--profile",
        default=None,
        help="Goal profile: short name under config/profiles/ (e.g. metadata), "
             "or path to a profile YAML. Default: config/profile.yaml.",
    )
    p.add_argument(
        "--backend",
        choices=backends,
        default=app.models.task_backend,
        help=f"Provider for the generation LM: {' | '.join(backends)}.",
    )
    p.add_argument(
        "--task-model",
        default=None,
        help="Override generation model slug for --backend "
             "(else config backends.<b>.task_model).",
    )
    p.add_argument("--seed", type=int, default=app.run.seed)
    p.add_argument("--num-threads", type=int, default=app.run.num_threads)
    p.add_argument(
        "--auto",
        choices=["light", "medium", "heavy"],
        default=app.run.auto,
    )
    p.add_argument(
        "--gepa-budget",
        type=int,
        default=app.run.gepa_budget,
        help="Cap GEPA at N metric evaluations (rollouts) instead of the auto preset.",
    )
    p.add_argument(
        "--judge",
        choices=["task", "reflection"],
        default=app.models.judge,
        help="Which LM scores alignment (default from config models.judge).",
    )
    p.add_argument(
        "--reflection-backend",
        choices=backends,
        default=app.models.reflection_backend,
        help="Provider for the GEPA reflection / reflection-judge LM.",
    )
    p.add_argument(
        "--reflection-model",
        default=None,
        help="Reflection model slug; defaults to config backends.<b>.reflection_model.",
    )
    p.add_argument(
        "--workdir",
        default=None,
        help="Default root for both input and output files "
        f"(default: {pathconf.DEFAULT_ARTIFACTS}). "
        "Use a separate workdir per goal/run.",
    )
    p.add_argument(
        "--inputdir",
        default=None,
        help="Read blueprint.md and scenarios-*.json from this directory "
        "(default: --workdir).",
    )
    p.add_argument(
        "--outputdir",
        default=None,
        help="Write programs, comparison, report, scenario gen, and blueprint "
        "cache here (default: --workdir).",
    )


def build_parser(app) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser(
        "gen-scenarios",
        help="LM-brainstorm scenarios into scenarios-<profile>.json (outputdir)",
    )
    gen.add_argument("--n", type=int, default=40)
    _add_common(gen, app)
    gen.set_defaults(func=cmd_gen_scenarios)

    for name in ("baseline", "bootstrap", "mipro", "gepa"):
        p = sub.add_parser(name, help=f"Run the {name} branch and evaluate it")
        _add_common(p, app)
        p.set_defaults(func=cmd_single)

    comp = sub.add_parser("compare", help="Run all branches and print a comparison table")
    _add_common(comp, app)
    comp.set_defaults(func=cmd_compare)

    ev = sub.add_parser(
        "eval",
        help="Evaluate a saved compiled program (same profile it was built with)",
    )
    ev.add_argument("--program", required=True)
    _add_common(ev, app)
    ev.set_defaults(func=cmd_eval)

    sp = sub.add_parser(
        "show-prompt",
        help="Print the seed prompt, and (with --program) the optimized one",
    )
    sp.add_argument(
        "--program",
        default=None,
        help="A saved program (e.g. artifacts/api-gepa.json) to show the optimized prompt from.",
    )
    _add_common(sp, app)
    sp.set_defaults(func=cmd_show_prompt)

    rp = sub.add_parser(
        "report",
        help="Write report-<profile>.md from existing comparison + programs in outputdir",
    )
    _add_common(rp, app)
    rp.set_defaults(func=cmd_report)

    return parser


def main() -> None:
    config_path = _early_flag(None, "config")
    profile_arg = _early_flag(None, "profile")
    app, _pc = _load_and_activate(config_path, profile_arg)
    parser = build_parser(app)
    args = parser.parse_args()
    # Subcommand may re-specify --config / --profile after the early parse.
    need_reload = False
    if getattr(args, "config", None) and args.config != config_path:
        need_reload = True
        config_path = args.config
    if getattr(args, "profile", None) and args.profile != profile_arg:
        need_reload = True
        profile_arg = args.profile
    if need_reload:
        app, _pc = _load_and_activate(config_path, profile_arg)
    args.func(args, app)


if __name__ == "__main__":
    main()
