#!/usr/bin/env python3
"""Re-run the ImmPort RA + female + ELISA cohort search.

Search is public (no key). Study summaries and ELISA result rows need
an ImmPort API key.

Get a key: https://www.immport.org/auth/api/keys
Use only the `api_key` string from the downloaded JSON, not the whole file.

    export IMMPORT_API_KEY='paste-api-key-here'
    python src/immport/search_ra_elisa.py

Or pass --api-key, or put IMMPORT_API_KEY=... in a .env file in this
directory or the repo root.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://www.immport.org/data/query"

STUDY_FIELDS = [
    "study_accession",
    "brief_title",
    "actual_enrollment",
    "assay_method",
    "study_pi",
    "doi",
    "clinical_trial",
    "program_name",
    "condition_or_disease",
]
SUBJECT_FIELDS = [
    "study_accession",
    "subject_accession",
    "sex",
    "min_age",
    "max_age",
    "race",
    "ethnicity",
    "assay_method",
    "biosample_type",
    "clinical_trial",
]


def load_dotenv() -> None:
    """Load KEY=VALUE lines from nearby .env files if the var is unset."""
    here = Path(__file__).resolve()
    candidates = [
        Path.cwd() / ".env",
        here.parent / ".env",
        here.parents[2] / ".env",
    ]
    for path in candidates:
        if not path.is_file():
            continue
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key, value = key.strip(), value.strip().strip("'\"")
            if key and key not in os.environ:
                os.environ[key] = value


def get_api_key(cli_value: str | None) -> str | None:
    raw = (cli_value or os.environ.get("IMMPORT_API_KEY") or "").strip()
    if not raw:
        return None
    if os.path.isfile(raw):
        raw = Path(raw).read_text(encoding="utf-8").strip()
    if raw.startswith("{"):
        try:
            blob = json.loads(raw)
        except json.JSONDecodeError:
            return raw
        extracted = blob.get("api_key") if isinstance(blob, dict) else None
        return extracted.strip() if isinstance(extracted, str) and extracted.strip() else None
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in "\"'":
        return raw[1:-1]
    return raw


def request_json(url: str, api_key: str | None = None) -> dict | list:
    headers = {"Accept": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        raise SystemExit(f"HTTP {exc.code} for {url}\n{body}") from exc


def search_url(kind: str, filters: dict[str, str], fields: list[str], page_size: int) -> str:
    params = {**filters, "pageSize": str(page_size), "sourceFields": ",".join(fields)}
    return f"{BASE}/api/search/{kind}?{urllib.parse.urlencode(params)}"


def hits_of(payload: dict) -> tuple[int, list[dict]]:
    hits = payload.get("hits", {})
    total = hits.get("total", {})
    n = total.get("value", 0) if isinstance(total, dict) else int(total or 0)
    sources = [h.get("_source", {}) for h in hits.get("hits", [])]
    return n, sources


def print_studies(studies: list[dict]) -> None:
    for s in studies:
        acc = s.get("study_accession", "?")
        title = s.get("brief_title", "")
        n = s.get("actual_enrollment", "?")
        doi = s.get("doi")
        assays = ", ".join(s.get("assay_method") or [])
        pis = "; ".join(s.get("study_pi") or [])
        print(f"  {acc}  n={n}  {title}")
        if pis:
            print(f"         PI: {pis}")
        if assays:
            print(f"         assays: {assays}")
        if doi:
            print(f"         doi: https://doi.org/{doi}")


def print_subjects(subjects: list[dict], limit: int) -> None:
    for s in subjects[:limit]:
        acc = s.get("subject_accession", "?")
        study = s.get("study_accession", "?")
        age = s.get("min_age")
        race = s.get("race", "")
        eth = s.get("ethnicity", "")
        print(f"  {acc}  {study}  age={age}  {race}  {eth}")
    if len(subjects) > limit:
        print(f"  … {len(subjects) - limit} more (use --json to dump all)")


def fetch_summary(study: str, api_key: str) -> dict:
    return request_json(f"{BASE}/api/study/summary/{study}", api_key)


def fetch_elisa(study: str, api_key: str, sex: str | None) -> list:
    # /result/elisa 500s if you pass sex=; filter client-side instead.
    url = f"{BASE}/result/elisa?{urllib.parse.urlencode({'studyAccession': study})}"
    payload = request_json(url, api_key)
    if isinstance(payload, list):
        rows = payload
    elif isinstance(payload, dict):
        rows = next(
            (payload[k] for k in ("data", "results", "hits") if isinstance(payload.get(k), list)),
            [payload],
        )
    else:
        rows = []
    if sex:
        want = sex.casefold()
        rows = [r for r in rows if str(r.get("gender") or r.get("sex") or "").casefold() == want]
    return rows


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    p.add_argument("--condition", default="rheumatoid arthritis")
    p.add_argument("--sex", default="Female")
    p.add_argument("--assay", default="ELISA")
    p.add_argument("--species", default="Homo sapiens")
    p.add_argument("--page-size", type=int, default=100)
    p.add_argument("--api-key", help="ImmPort api_key string (else IMMPORT_API_KEY)")
    p.add_argument("--elisa", action="store_true", help="Pull ELISA rows (requires API key)")
    p.add_argument("--json", metavar="PATH", help="Write the full result payload as JSON")
    return p.parse_args()


def main() -> int:
    load_dotenv()
    args = parse_args()
    api_key = get_api_key(args.api_key)

    filters = {
        "conditionOrDisease": args.condition,
        "sex": args.sex,
        "assayMethod": args.assay,
        "species": args.species,
    }

    print("Searching ImmPort")
    for k, v in filters.items():
        print(f"  {k} = {v}")
    print(f"  API key: {'set' if api_key else 'not set (search only)'}")
    print()

    study_payload = request_json(search_url("study", filters, STUDY_FIELDS, args.page_size))
    subject_payload = request_json(search_url("subject", filters, SUBJECT_FIELDS, args.page_size))
    n_studies, studies = hits_of(study_payload)
    n_subjects, subjects = hits_of(subject_payload)

    print(f"Studies: {n_studies}")
    print_studies(studies)
    print()
    print(f"Subjects: {n_subjects}")
    print_subjects(subjects, limit=15)

    out = {
        "filters": filters,
        "study_total": n_studies,
        "subject_total": n_subjects,
        "studies": studies,
        "subjects": subjects,
        "summaries": {},
        "elisa": {},
    }

    accessions = [s.get("study_accession") for s in studies if s.get("study_accession")]
    if args.elisa and not api_key:
        print("\n--elisa needs IMMPORT_API_KEY (or --api-key).", file=sys.stderr)
        return 2
    if api_key and accessions:
        print()
        for acc in accessions:
            try:
                summary = fetch_summary(acc, api_key)
            except SystemExit as exc:
                print(f"Summary {acc} failed:\n{exc}", file=sys.stderr)
                continue
            out["summaries"][acc] = summary
            title = summary.get("title") or summary.get("briefTitle") or acc
            n = summary.get("subjectsNumber", "?")
            print(f"Summary {acc}: {title}  subjects={n}")
            if args.elisa:
                try:
                    rows = fetch_elisa(acc, api_key, args.sex)
                except SystemExit as exc:
                    print(f"  ELISA {acc} failed:\n{exc}", file=sys.stderr)
                    continue
                out["elisa"][acc] = rows
                print(f"  ELISA rows ({args.sex}): {len(rows)}")

    if args.json:
        Path(args.json).write_text(json.dumps(out, indent=2), encoding="utf-8")
        print(f"\nWrote {args.json}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
