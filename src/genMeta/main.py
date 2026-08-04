#!/usr/bin/env python3
"""genMeta — Herdr + Pi extract → host SHACL validate → repair loop.

First-try pipeline for NIAID Blueprint Dataset JSON-LD generation.
Does not use Hermes. Transport: herdr-python-client (Unix socket).

Usage (from repo root, with Herdr running)::

    uv run python src/genMeta/main.py --url https://example.org/dataset
    uv run python src/genMeta/main.py --url … --max-iters 3 --cleanup
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

# Allow ``from defs…`` when run as a script from src/genMeta or via path.
_GENMETA_DIR = Path(__file__).resolve().parent
if str(_GENMETA_DIR) not in sys.path:
    sys.path.insert(0, str(_GENMETA_DIR))

from herdr_client import HerdrApiError, HerdrClientError  # noqa: E402

from defs import artifacts  # noqa: E402
from defs.config import (  # noqa: E402
    AGENTS,
    REPO_ROOT,
    ROLE_EXTRACTOR,
    ROLE_REPAIRER,
    render_prompt,
)
from defs.herdr import (  # noqa: E402
    AgentSession,
    clear_session_registry,
    close_workspace,
    create_workspace,
    ensure_agent_name,
    ensure_reachable,
    free_agent_names,
    list_agents,
    split_pane,
    start_agent,
)
from defs.report import write_final_report  # noqa: E402
from defs.task import (  # noqa: E402
    resolve_max_iters,
    resolve_models,
    resolve_runs_dir,
    resolve_timeout,
    warn_openrouter_credentials,
)
from defs.validate_host import run_host_validation  # noqa: E402


def _load_system(name: str) -> str:
    return render_prompt(name)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="genMeta: Herdr+Pi extract → SHACL validate → repair until pass",
    )
    parser.add_argument("--url", required=True, help="Resource URL to extract metadata from")
    parser.add_argument("--max-iters", type=int, default=None, help="Max validate/repair iterations")
    parser.add_argument("--timeout", type=int, default=None, help="Settle timeout per agent turn (s)")
    parser.add_argument("--runs-dir", default=None, help="Root directory for run artifacts")
    parser.add_argument("--model-extractor", default=None, help="Pi model id for extractor")
    parser.add_argument("--model-repairer", default=None, help="Pi model id for repairer")
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Close Herdr workspace when finished",
    )
    parser.add_argument(
        "--cwd",
        default=None,
        help="Working directory for Herdr panes (default: repo root)",
    )
    args = parser.parse_args(argv)

    url = args.url.strip()
    if not url.startswith("http"):
        print("error: --url must be an http(s) URL", file=sys.stderr)
        return 2

    max_iters = resolve_max_iters(args.max_iters)
    timeout_s = resolve_timeout(args.timeout)
    runs_root = resolve_runs_dir(args.runs_dir)
    models = resolve_models(args.model_extractor, args.model_repairer)
    warn_openrouter_credentials(models)

    cwd = Path(args.cwd).resolve() if args.cwd else REPO_ROOT
    if not cwd.is_dir():
        print(f"error: cwd does not exist: {cwd}", file=sys.stderr)
        return 2

    run_dir = artifacts.new_run_dir(runs_root)
    label = run_dir.name
    artifacts.write_task_snapshot(
        run_dir,
        url=url,
        models=models,
        max_iters=max_iters,
        repo_root=REPO_ROOT,
    )

    print(f"Repo      : {REPO_ROOT}")
    print(f"CWD       : {cwd}")
    print(f"Run       : {run_dir}")
    print(f"URL       : {url}")
    print(f"Models    : {models}")
    print(f"Max iters : {max_iters}")
    print()

    try:
        ensure_reachable()
    except (FileNotFoundError, HerdrClientError, OSError):
        print(
            "Herdr server is not reachable.\n"
            "Start it with:  herdr\n"
            "or headless:    herdr server &",
            file=sys.stderr,
        )
        return 1

    # ------------------------------------------------------------------
    # Workspace + panes
    # ------------------------------------------------------------------
    print("==> Creating workspace…")
    create = create_workspace(cwd=cwd, label=label, focus=False)
    ws_id = create["workspace"]["workspace_id"]
    root_pane = create["root_pane"]["pane_id"]
    (run_dir / "workspace_id").write_text(ws_id + "\n", encoding="utf-8")
    print(f"  workspace_id = {ws_id}")
    print(f"  root_pane    = {root_pane}")

    print("\n==> Freeing agent names…")
    free_agent_names(AGENTS)
    clear_session_registry()

    print("\n==> Building pane layout…")
    pane_extractor = root_pane
    pane_repairer = split_pane(pane_extractor, "right", cwd=cwd)
    print(f"  extractor={pane_extractor} repairer={pane_repairer}")

    print("\n==> Spawning Pi agents…")
    sessions: dict[str, AgentSession] = {}
    sessions[ROLE_EXTRACTOR] = start_agent(
        ROLE_EXTRACTOR,
        _load_system("extractor_system.md"),
        pane_id=pane_extractor,
        model=models[ROLE_EXTRACTOR],
    )
    sessions[ROLE_REPAIRER] = start_agent(
        ROLE_REPAIRER,
        _load_system("repairer_system.md"),
        pane_id=pane_repairer,
        model=models[ROLE_REPAIRER],
    )

    for name in AGENTS:
        sessions[name].wait_until_idle(timeout_s=90)

    print("\n==> Verifying agent aliases…")
    live = {a.get("pane_id"): a for a in list_agents()}
    for name, session in sessions.items():
        ensure_agent_name(session.pane_id, name)
        info = session.refresh()
        ok = info.get("name") == name and info.get("agent") == "pi"
        mark = "OK" if ok else "BAD"
        print(
            f"  [{mark}] {name:20} pane={session.pane_id} "
            f"alias={info.get('name')!r} kind={info.get('agent')!r}"
        )
        if not ok:
            raise RuntimeError(f"agent {name!r} not ready as pi with alias")

    iterations: list[dict] = []
    final_conforms = False
    record: Path | None = None

    try:
        # ------------------------------------------------------------------
        # PHASE 1 — Extract
        # ------------------------------------------------------------------
        print("\n==> PHASE 1: extract (Pi)")
        extract_prompt = render_prompt(
            "extractor_user.md",
            url=url,
            run_dir=str(run_dir),
        )
        extractor = sessions[ROLE_EXTRACTOR]
        extractor.refresh()
        base_rev = extractor.revision
        extractor.submit(extract_prompt)
        if not extractor.wait_settled(timeout_s=timeout_s, base_revision=base_rev):
            raise TimeoutError(f"extractor did not settle within {timeout_s}s")
        extractor.save_notes(run_dir / "01-extractor.txt")
        transcript = (run_dir / "01-extractor.txt").read_text(encoding="utf-8")
        record = artifacts.ensure_record_jsonld(run_dir, transcript=transcript)
        print(f"  record → {record}")

        # ------------------------------------------------------------------
        # PHASE 2/3 — Validate / Repair loop
        # ------------------------------------------------------------------
        for iteration in range(1, max_iters + 1):
            print(f"\n==> PHASE 2: validate (host) iter={iteration}")
            out_dir = artifacts.validation_iter_dir(run_dir, iteration)
            summary = run_host_validation(record, out_dir)
            sample = (summary.get("results") or [])[:8]
            iterations.append(
                {
                    "iteration": iteration,
                    "conforms": summary.get("conforms"),
                    "n_violations": summary.get("n_violations"),
                    "out_dir": str(out_dir),
                    "sample_findings": sample,
                }
            )

            if summary.get("conforms"):
                final_conforms = True
                print("  CONFORMS — stopping loop")
                break

            if iteration >= max_iters:
                print("  max iterations reached without conformance")
                break

            print(f"\n==> PHASE 3: repair (Pi) iter={iteration}")
            repairer = sessions[ROLE_REPAIRER]
            try:
                repairer.refresh()
            except RuntimeError as exc:
                raise RuntimeError(f"repairer pane lost: {exc}") from exc
            try:
                ensure_agent_name(repairer.pane_id, ROLE_REPAIRER)
            except (HerdrApiError, HerdrClientError, RuntimeError) as exc:
                print(f"  warning: could not re-bind repairer alias: {exc}")

            results_json = out_dir / "results.json"
            conforms_json = out_dir / "conforms.json"
            repair_prompt = render_prompt(
                "repairer_user.md",
                url=url,
                run_dir=str(run_dir),
                iteration=str(iteration),
                results_json=str(results_json),
                conforms_json=str(conforms_json),
            )
            repairer.refresh()
            repair_base = repairer.revision
            repairer.submit(repair_prompt)
            if not repairer.wait_settled(timeout_s=timeout_s, base_revision=repair_base):
                raise TimeoutError(f"repairer did not settle within {timeout_s}s")
            repair_notes = run_dir / f"02-repair-iter-{iteration:02d}.txt"
            repairer.save_notes(repair_notes)
            transcript = repair_notes.read_text(encoding="utf-8")
            record = artifacts.ensure_record_jsonld(run_dir, transcript=transcript)
            print(f"  record updated → {record}")

    finally:
        # ------------------------------------------------------------------
        # Report + optional cleanup
        # ------------------------------------------------------------------
        print("\n==> Writing report…")
        write_final_report(
            run_dir / "final-report.md",
            url=url,
            label=label,
            ws_id=ws_id,
            models=models,
            run_dir=run_dir,
            iterations=iterations,
            final_conforms=final_conforms,
            record_path=record,
        )

        cleanup = args.cleanup or os.environ.get("GENMETA_CLEANUP", "").lower() in (
            "1",
            "true",
            "yes",
        )
        if cleanup:
            print("\n==> Closing workspace…")
            close_workspace(ws_id, check=False)
        else:
            print("\nAgents left running for inspection.")
            print(f"  Close later with:  herdr workspace close {ws_id}")

    print("\n✅ genMeta complete")
    print(f"  run dir:  {run_dir}")
    print(f"  report:   {run_dir / 'final-report.md'}")
    print(f"  conforms: {final_conforms}")
    return 0 if final_conforms else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\ninterrupted", file=sys.stderr)
        raise SystemExit(130)
