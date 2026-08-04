"""CLI for libraryOptimizer: GEPA-optimize one OKF library prompt example.

    uv run python src/libraryOptimizer/main.py list-prompts
    uv run python src/libraryOptimizer/main.py gen-scenarios --prompt path/to/example.md
    uv run python src/libraryOptimizer/main.py optimize --prompt path/to/example.md --gepa-budget 40
    uv run python src/libraryOptimizer/main.py baseline --prompt path/to/example.md
    uv run python src/libraryOptimizer/main.py show-prompt --prompt path/to/example.md
    uv run python src/libraryOptimizer/main.py show-prompt --prompt path/to/example.md \\
        --program artifacts/<slug>-gepa.json
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import dspy

# Package root on sys.path so `defs` / `optimize` resolve when run as a script.
_PKG = Path(__file__).resolve().parent
if str(_PKG) not in sys.path:
    sys.path.insert(0, str(_PKG))

from defs import paths as pathconf  # noqa: E402
from defs.config import (  # noqa: E402
    announce_config,
    get_active_config,
    load_app_config,
    set_active_config,
)
from defs.dataset import build_examples, ensure_scenarios, generate_scenarios  # noqa: E402
from defs.evaluate import RunResult  # noqa: E402
from defs.guidance import build_guidance_context, clear_guidance_cache  # noqa: E402
from defs.lm import (  # noqa: E402
    BACKENDS,
    get_reflection_lm,
    get_task_lm,
    refresh_backends,
)
from defs.load_prompt import list_prompt_files, load_library_prompt  # noqa: E402
from defs.metric import set_judge_lm  # noqa: E402
from defs.prompts import instructions_text, optimized_prompt, seed_prompt  # noqa: E402
from defs.report import write_report  # noqa: E402
from defs.task import task_from_prompt  # noqa: E402
from optimize import baseline, gepa  # noqa: E402


def _score_of(result) -> float:
    return float(getattr(result, "score", result)) / 100.0


def _load_app(config_path: str | None):
    app = load_app_config(config_path)
    set_active_config(app)
    refresh_backends(app)
    announce_config(app)
    return app


def _configure_paths(args) -> None:
    pathconf.configure_paths(
        workdir=getattr(args, "workdir", None),
        inputdir=getattr(args, "inputdir", None),
        outputdir=getattr(args, "outputdir", None),
    )


def _api_base_of(args) -> str | None:
    return getattr(args, "api_base", None)


def _configure_lms(args, app, *, need_judge: bool = True) -> None:
    dspy.configure_cache(enable_disk_cache=False, enable_memory_cache=False)
    dspy.configure(
        lm=get_task_lm(
            args.backend,
            model=getattr(args, "task_model", None),
            api_base=_api_base_of(args),
            cfg=app,
        )
    )
    if not need_judge:
        set_judge_lm(None)
    elif getattr(args, "judge", "reflection") == "reflection":
        set_judge_lm(
            get_reflection_lm(
                args.reflection_backend,
                model=args.reflection_model,
                api_base=_api_base_of(args),
                cfg=app,
            )
        )
    else:
        set_judge_lm(None)


def _init_guidance(args, app) -> None:
    clear_guidance_cache()
    bp = (
        Path(args.blueprint_path).expanduser().resolve()
        if getattr(args, "blueprint_path", None)
        else app.guidance.blueprint
    )
    wp = (
        Path(args.workplans_path).expanduser().resolve()
        if getattr(args, "workplans_path", None)
        else app.guidance.workplans
    )
    build_guidance_context(
        blueprint_path=bp,
        workplans_path=wp,
        keep_keywords=app.guidance.keep_keywords or None,
        max_chars=app.guidance.max_chars,
        refresh=bool(getattr(args, "refresh_guidance", False)),
    )


def _load_task(args, app):
    if not getattr(args, "prompt", None):
        raise SystemExit("--prompt is required (path to an OKF prompt example .md)")
    lp = load_library_prompt(
        args.prompt,
        examples_root=app.prompts.examples_root,
    )
    return task_from_prompt(lp), lp


def cmd_list_prompts(args, app) -> None:
    root = app.prompts.examples_root
    files = list_prompt_files(root)
    if not files:
        print(f"No prompt examples under {root}")
        return
    print(f"Prompt examples under {root}:\n")
    for p in files:
        try:
            rel = p.relative_to(root)
        except ValueError:
            rel = p
        print(f"  {rel}")
    print(f"\n{len(files)} file(s). Use --prompt <path> with optimize / gen-scenarios.")


def cmd_gen_scenarios(args, app) -> None:
    task, lp = _load_task(args, app)
    _configure_paths(args)
    _configure_lms(args, app, need_judge=False)
    n = args.n if args.n is not None else app.data.n_scenarios
    scenarios = generate_scenarios(task, n=n)
    out = pathconf.scenarios_write_path(task.name)
    print(f"Wrote {len(scenarios)} scenarios to {out}\n")
    for i, s in enumerate(scenarios, 1):
        print(f"{i:2d}. {s[:120]}{'…' if len(s) > 120 else ''}")


def _prepare_data(args, app, task):
    _configure_paths(args)
    _configure_lms(args, app, need_judge=True)
    _init_guidance(args, app)
    n = args.n if getattr(args, "n", None) is not None else None
    ensure_scenarios(task, n=n)
    trainset, valset, testset = build_examples(task, seed=args.seed)
    return trainset, valset, testset


def cmd_baseline(args, app) -> None:
    task, lp = _load_task(args, app)
    trainset, valset, testset = _prepare_data(args, app, task)
    start = time.perf_counter()
    result, path, _ = baseline.run(
        task=task,
        trainset=trainset,
        valset=valset,
        testset=testset,
        num_threads=args.num_threads,
    )
    seconds = time.perf_counter() - start
    score = _score_of(result)
    report = write_report(
        pathconf.report_path(task.name),
        slug=task.name,
        source_prompt=str(lp.path),
        branch="baseline",
        score=score,
        seconds=seconds,
        n_train=len(trainset),
        n_val=len(valset),
        n_test=len(testset),
        program_path=path,
        optimized_prompt_path=None,
        notes="Seed program (library prompt body as instructions), no GEPA.",
    )
    print(f"baseline score={score:.4f} seconds={seconds:.1f} program={path}")
    print(f"report={report}")


def cmd_optimize(args, app) -> None:
    task, lp = _load_task(args, app)
    trainset, valset, testset = _prepare_data(args, app, task)
    reflection_lm = get_reflection_lm(
        args.reflection_backend,
        model=args.reflection_model,
        api_base=_api_base_of(args),
        cfg=app,
    )
    budget = args.gepa_budget if args.gepa_budget is not None else app.run.gepa_budget
    start = time.perf_counter()
    result, path, opt_md = gepa.run(
        task=task,
        trainset=trainset,
        valset=valset,
        testset=testset,
        num_threads=args.num_threads,
        auto=args.auto,
        reflection_lm=reflection_lm,
        gepa_budget=budget,
    )
    seconds = time.perf_counter() - start
    score = _score_of(result)
    report = write_report(
        pathconf.report_path(task.name),
        slug=task.name,
        source_prompt=str(lp.path),
        branch="gepa",
        score=score,
        seconds=seconds,
        n_train=len(trainset),
        n_val=len(valset),
        n_test=len(testset),
        program_path=path,
        optimized_prompt_path=opt_md,
        notes=f"GEPA budget={budget!r} auto={args.auto!r}",
    )
    print(f"gepa score={score:.4f} seconds={seconds:.1f} program={path}")
    if opt_md:
        print(f"optimized_prompt={opt_md}")
    print(f"report={report}")


def cmd_show_prompt(args, app) -> None:
    task, lp = _load_task(args, app)
    if getattr(args, "program", None):
        path = pathconf.resolve_program_arg(args.program)
        parts = optimized_prompt(task, str(path))
        label = f"program {path}"
    else:
        parts = seed_prompt(task)
        label = f"seed from {lp.path}"
    text = instructions_text(parts)
    print(f"# {label}\n")
    print(text if text else "(empty instructions)")


def _add_shared_flags(p: argparse.ArgumentParser, backends: tuple[str, ...]) -> None:
    p.add_argument("--config", default=None, help="Config dir or default.yaml path")
    p.add_argument("--prompt", default=None, help="Path to OKF prompt example .md")
    p.add_argument(
        "--backend",
        default=None,
        choices=backends if backends else None,
        help="Task LM backend (default from config)",
    )
    p.add_argument("--task-model", default=None, dest="task_model")
    p.add_argument(
        "--reflection-backend",
        default=None,
        dest="reflection_backend",
        choices=backends if backends else None,
    )
    p.add_argument("--reflection-model", default=None, dest="reflection_model")
    p.add_argument("--api-base", default=None, dest="api_base")
    p.add_argument(
        "--judge",
        default="reflection",
        choices=("reflection", "task"),
        help="Which LM grades artifacts (default: reflection)",
    )
    p.add_argument("--workdir", default=None)
    p.add_argument("--inputdir", default=None)
    p.add_argument("--outputdir", default=None)
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--num-threads", type=int, default=None, dest="num_threads")
    p.add_argument("--auto", default=None, choices=("light", "medium", "heavy"))
    p.add_argument("--gepa-budget", type=int, default=None, dest="gepa_budget")
    p.add_argument("--n", type=int, default=None, help="Scenario count for gen / auto-gen")
    p.add_argument("--blueprint-path", default=None, dest="blueprint_path")
    p.add_argument("--workplans-path", default=None, dest="workplans_path")
    p.add_argument(
        "--refresh-guidance",
        action="store_true",
        dest="refresh_guidance",
        help="Rebuild guidance.md cache from source docs",
    )


def _apply_config_defaults(args, app) -> None:
    if args.backend is None:
        args.backend = app.models.task_backend
    if args.reflection_backend is None:
        args.reflection_backend = app.models.reflection_backend
    if args.seed is None:
        args.seed = app.run.seed
    if args.num_threads is None:
        args.num_threads = app.run.num_threads
    if args.auto is None:
        args.auto = app.run.auto
    if getattr(args, "judge", None) is None:
        args.judge = app.models.judge


def build_parser(backends: tuple[str, ...] | None = None) -> argparse.ArgumentParser:
    backends = backends or BACKENDS
    parser = argparse.ArgumentParser(
        description="Optimize OKF library prompt examples with DSPy GEPA "
        "against NIAID Blueprint + Work Plans guidance."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list-prompts", help="List OKF prompt example files")
    _add_shared_flags(p_list, backends)

    p_gen = sub.add_parser("gen-scenarios", help="Brainstorm and save scenarios for a prompt")
    _add_shared_flags(p_gen, backends)

    p_base = sub.add_parser("baseline", help="Score seed program once (no GEPA)")
    _add_shared_flags(p_base, backends)

    p_opt = sub.add_parser("optimize", help="Run GEPA on one library prompt")
    _add_shared_flags(p_opt, backends)

    p_show = sub.add_parser("show-prompt", help="Print seed or compiled instructions")
    _add_shared_flags(p_show, backends)
    p_show.add_argument(
        "--program",
        default=None,
        help="Compiled program JSON (e.g. artifacts/<slug>-gepa.json)",
    )

    return parser


def main(argv: list[str] | None = None) -> None:
    # Early config so --backend choices match YAML
    early = argparse.ArgumentParser(add_help=False)
    early.add_argument("--config", default=None)
    early_args, _ = early.parse_known_args(argv)
    app = _load_app(early_args.config)
    backends = app.backend_names()

    parser = build_parser(backends)
    args = parser.parse_args(argv)
    _apply_config_defaults(args, app)

    commands = {
        "list-prompts": cmd_list_prompts,
        "gen-scenarios": cmd_gen_scenarios,
        "baseline": cmd_baseline,
        "optimize": cmd_optimize,
        "show-prompt": cmd_show_prompt,
    }
    commands[args.command](args, app)


if __name__ == "__main__":
    main()
