"""CLI: URL (and optional files) → CEDAR template instance JSON-LD."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_PKG = Path(__file__).resolve().parent
if str(_PKG) not in sys.path:
    sys.path.insert(0, str(_PKG))

from defs.cedar_jsonld import cedar_to_record, record_to_cedar  # noqa: E402
from defs.compare import compare_records, format_table  # noqa: E402
from defs.fetch import FetchSession, ObscuraClient  # noqa: E402
from defs.lm import BACKENDS, configure_lm  # noqa: E402
from defs.notes import render_notes  # noqa: E402
from defs.program import CedarExtract  # noqa: E402
from defs.progress import enable as enable_debug, say  # noqa: E402


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Extract NIAID Blueprint / CEDAR dataset metadata from a URL."
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    extract = sub.add_parser("extract", help="Fetch, extract, write record.jsonld")
    extract.add_argument("--url", help="Landing-page URL")
    extract.add_argument(
        "--file",
        action="append",
        default=[],
        help="Extra local document (repeatable). Counts as evidence, not crawl budget.",
    )
    extract.add_argument("--out", required=True, help="Output directory")
    extract.add_argument("--backend", choices=BACKENDS, default="nrp")
    extract.add_argument("--task-model", dest="task_model")
    extract.add_argument("--api-base")
    extract.add_argument("--obscura-bin")
    extract.add_argument("--max-depth", type=int, default=2)
    extract.add_argument("--max-pages", type=int, default=5)
    extract.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch the start URL (and files) only; do not call the LM.",
    )
    extract.add_argument("--timeout", type=int, default=30, help="Obscura per-page timeout seconds")
    extract.add_argument(
        "--debug",
        action="store_true",
        help="Print timestamped progress on stdout (fetch, gather, each extract, write).",
    )
    extract.add_argument(
        "--compare",
        help="Path to a gold CEDAR JSON-LD instance; print a payload field table after extract.",
    )
    return p


def _print_corpus(session: FetchSession) -> None:
    print(f"pages: {len(session.pages)}")
    for page in session.pages:
        flag = "ok" if page.ok else f"ERR {page.error}"
        print(
            f"  d{page.depth} {page.url} [{flag}] "
            f"md={len(page.markdown)} jsonld={len(page.jsonld_blocks)} links={len(page.links)}"
        )


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.cmd != "extract":
        return 2
    if not args.url and not args.file:
        print("error: provide --url and/or --file", file=sys.stderr)
        return 2

    if args.debug:
        enable_debug()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    say(
        f"extract backend={args.backend} model={args.task_model or '(default)'} "
        f"max-depth={args.max_depth} max-pages={args.max_pages} "
        f"url={args.url or '(none)'}"
    )
    client = ObscuraClient(bin_path=args.obscura_bin, timeout=args.timeout)
    say(f"obscura bin={client.bin_path} timeout={client.timeout}s")
    session = FetchSession(client, max_depth=args.max_depth, max_pages=args.max_pages)
    for raw in args.file:
        say(f"load file {raw}")
        session.add_local_file(Path(raw))

    if args.dry_run:
        if args.url:
            session.fetch(args.url, depth=0)
        _print_corpus(session)
        return 0

    say("configure LM")
    lm = configure_lm(args.backend, model=args.task_model, api_base=args.api_base)
    say(f"LM ready: {getattr(lm, 'model', args.task_model or args.backend)}")
    program = CedarExtract(session)
    # ReAct gather cannot fetch extra pages when depth/budget is already exhausted.
    skip_gather = (not args.url) or args.max_depth <= 0 or args.max_pages <= 1
    pred = program(start_url=args.url, skip_gather=skip_gather)
    record = pred.record
    say("serialize CEDAR JSON-LD")
    doc = record_to_cedar(record)
    record_path = out / "record.jsonld"
    notes_path = out / "notes.md"
    record_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    notes_path.write_text(
        render_notes(
            start_url=args.url,
            pages=list(pred.pages),
            notes=list(pred.notes),
            dropped=list(pred.dropped),
            evidence_summary=pred.evidence_summary,
        ),
        encoding="utf-8",
    )
    say(f"wrote {record_path}")
    say(f"wrote {notes_path}")
    if not args.debug:
        print(f"wrote {record_path}")
        print(f"wrote {notes_path}")
    _print_corpus(session)
    if args.compare:
        gold_doc = json.loads(Path(args.compare).read_text(encoding="utf-8"))
        gold = cedar_to_record(gold_doc)
        table = format_table(compare_records(gold, record))
        compare_path = out / "compare.md"
        compare_path.write_text(table, encoding="utf-8")
        print(table)
        say(f"wrote {compare_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
