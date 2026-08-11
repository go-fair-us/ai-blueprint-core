#!/usr/bin/env python3
"""genMeta — Herdr + Pi extract → host SHACL validate → repair loop.

First-try pipeline for NIAID Blueprint Dataset JSON-LD generation.
Does not use Hermes. Transport: herdr-python-client (Unix socket).

Pipeline (single handoff; no re-submit of the extract URL)::

    URL → Pi extractor (once) → record.jsonld + notes.md
        → host pySHACL
        → if fail: Pi repairer patches record → host pySHACL (repeat)
        → final-report.md

Usage (from repo root, with Herdr running)::

    uv run python src/genMeta/main.py --url https://example.org/dataset
    uv run python src/genMeta/main.py --url … --max-iters 3 --cleanup
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

# Allow ``from defs…`` when run as a script from src/genMeta or via path.
_GENMETA_DIR = Path(__file__).resolve().parent
if str(_GENMETA_DIR) not in sys.path:
    sys.path.insert(0, str(_GENMETA_DIR))

from herdr_client import HerdrApiError, HerdrClientError  # noqa: E402

from defs import artifacts  # noqa: E402
from defs.config import (  # noqa: E402
    AGENTS,
    PROMPTS_DIR,
    REPO_ROOT,
    ROLE_EXTRACTOR,
    ROLE_REPAIRER,
    assert_skill_paths,
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


def _system_prompt_path(name: str) -> Path:
    """Path to a system prompt file (passed to Pi via --append-system-prompt).

    Must be a path, not file contents: Herdr rejects multi-line agent args
    with invalid_agent_argument.
    """
    path = PROMPTS_DIR / name
    if not path.is_file():
        raise FileNotFoundError(f"System prompt not found: {path}")
    return path


def _save_transcript(session: AgentSession, path: Path) -> None:
    """Best-effort transcript dump (never aborts the pipeline)."""
    try:
        session.save_notes(path)
    except (HerdrApiError, HerdrClientError, RuntimeError, OSError) as exc:
        print(f"  warning: could not save transcript {path.name}: {exc}")


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

    try:
        assert_skill_paths()
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
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
        _system_prompt_path("extractor_system.md"),
        pane_id=pane_extractor,
        model=models[ROLE_EXTRACTOR],
    )
    sessions[ROLE_REPAIRER] = start_agent(
        ROLE_REPAIRER,
        _system_prompt_path("repairer_system.md"),
        pane_id=pane_repairer,
        model=models[ROLE_REPAIRER],
    )

    for name in AGENTS:
        sessions[name].wait_until_idle(timeout_s=90)

    print("\n==> Verifying agent aliases…")
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
    exit_code = 1

    try:
        # ------------------------------------------------------------------
        # PHASE 1 — Extract (once). Completion = artifacts on disk, not a
        # Herdr idle flake. The extractor is never re-prompted with the URL.
        # ------------------------------------------------------------------
        print("\n==> PHASE 1: extract (Pi) — single turn")
        extract_prompt = render_prompt(
            "extractor_user.md",
            url=url,
            run_dir=str(run_dir),
            run_id=label,
        )
        extractor = sessions[ROLE_EXTRACTOR]
        extractor.refresh()
        extract_submitted_at = time.time()
        extractor.submit(extract_prompt)
        print(
            f"  submitted extract task at {time.strftime('%H:%M:%S')}; "
            f"waiting for {artifacts.RECORD_NAME} + {artifacts.NOTES_NAME}…"
        )

        # Source of truth: files written under run_dir (not agent status alone).
        record = artifacts.wait_for_extract_artifacts(
            run_dir,
            not_before=extract_submitted_at,
            timeout_s=float(timeout_s),
            require_notes=True,
        )
        # Best-effort: let the agent finish its confirmation message.
        extractor.wait_idle_after(timeout_s=min(120.0, float(timeout_s)))
        _save_transcript(extractor, run_dir / "01-extractor.txt")
        record = artifacts.ensure_record_jsonld(run_dir)
        print(f"  record → {record} (extract complete; no re-submit)")

        # ------------------------------------------------------------------
        # PHASE 2/3 — Host SHACL validate / Pi repair loop
        #
        # SHACL always runs on the host (deterministic). The repairer only
        # patches record.jsonld from results.json — it does not re-extract.
        # ------------------------------------------------------------------
        for iteration in range(1, max_iters + 1):
            print(f"\n==> PHASE 2: validate (host pySHACL) iter={iteration}")
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
                run_id=label,
                iteration=str(iteration),
                results_json=str(results_json),
                conforms_json=str(conforms_json),
            )
            prev_mtime = artifacts.mtime(record)
            repairer.refresh()
            repair_submitted_at = time.time()
            repairer.submit(repair_prompt)
            print(
                f"  submitted repair iter={iteration}; "
                f"waiting for updated {artifacts.RECORD_NAME}…"
            )

            record = artifacts.wait_for_record_update(
                run_dir,
                previous_mtime=prev_mtime,
                not_before=repair_submitted_at,
                timeout_s=float(timeout_s),
            )
            repairer.wait_idle_after(timeout_s=min(120.0, float(timeout_s)))
            repair_notes = run_dir / f"02-repair-iter-{iteration:02d}.txt"
            _save_transcript(repairer, repair_notes)
            record = artifacts.ensure_record_jsonld(run_dir)
            print(f"  record updated → {record}")

        exit_code = 0 if final_conforms else 1

    except KeyboardInterrupt:
        print("\ninterrupted", file=sys.stderr)
        exit_code = 130
    except Exception as exc:
        print(f"\nerror during pipeline: {exc}", file=sys.stderr)
        exit_code = 1
    finally:
        # Prefer in-memory path; fall back to whatever the agents wrote on disk
        # so the report is useful after timeouts / mid-run failures.
        if record is None or not Path(record).is_file():
            disk = artifacts.record_path(run_dir)
            if disk.is_file():
                record = disk

        print("\n==> Writing report…")
        try:
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
        except OSError as exc:
            print(f"  warning: could not write report: {exc}")

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

    print("\n✅ genMeta complete" if exit_code in (0, 1) else "\n⏹ genMeta stopped")
    print(f"  run dir:  {run_dir}")
    print(f"  report:   {run_dir / 'final-report.md'}")
    print(f"  conforms: {final_conforms}")
    return exit_code


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\ninterrupted", file=sys.stderr)
        raise SystemExit(130)
