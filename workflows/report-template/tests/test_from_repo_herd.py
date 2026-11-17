"""Tests for tools/from_repo_herd.py and build.py --run.

    python3 -m pytest tests            # or: python3 tests/test_from_repo_herd.py

The real-run test needs a run folder. It uses $REPO_HERD_RUN, else
../repo_herd/repo_herd/runs/20261117T020206Z next to this kit, and is skipped if neither exists.
"""
import json
import os
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import from_repo_herd as frh  # noqa: E402
import build  # noqa: E402

SUMMARY = """# Repository herd summary

## Alpha Repository (ALPHA)

Facet origin: https://alpha.example.org/

| # | Property | Evaluation | Verdict | Evidence URL |
| --- | --- | --- | --- | --- |
| 1 | Be reachable | reachable-fetch | present | https://alpha.example.org/ |
| 2 | Be callable | mcp-exposure | not-observable (report did not include this evaluation) | https://alpha.example.org/ |
| 3 | Be callable | brand-new-check | blocked | https://alpha.example.org/x |

## Beta

Facet origin: https://beta.example.org/

| # | Property | Evaluation | Verdict | Evidence URL |
| --- | --- | --- | --- | --- |
| 1 | Be reachable | reachable-fetch | absent | https://beta.example.org/ |
| 2 | Be callable | mcp-exposure | maybe | https://beta.example.org/ |
| 3 | Be callable | brand-new-check | partial | https://beta.example.org/ |

Pi processes with a non-zero exit code: 1
"""

SCORE = """# Alpha answerability score

## run-a

Pi exit code: 0

| ID | Stability | Grade | Expected | Answer | Check |
| --- | --- | --- | --- | --- | --- |
| AL-1 | stable | match | x | x | contains: 'x' |
| AL-2 | stable | miss | y | z | contains: 'y' |

## run-b

Pi exit code: 1

| ID | Stability | Grade | Expected | Answer | Check |
| --- | --- | --- | --- | --- | --- |
| AL-3 | stable | no-answer | 1 |  | exact |
"""


def make_run(tmp: Path) -> Path:
    run = tmp / "20260102T030405Z"
    repos = [
        {"name": "Alpha Repository (ALPHA)", "slug": "alpha", "origin": "https://alpha.example.org/",
         "question_origin": "https://q.alpha.example.org/"},
        {"name": "Beta", "slug": "beta", "origin": "https://beta.example.org/",
         "question_origin": "https://beta.example.org/"},
    ]
    jobs = [{"id": "alpha-facet", "dir": "alpha/facet"}, {"id": "beta-facet", "dir": "beta/facet"},
            {"id": "alpha-a", "dir": "alpha/answerability/run-a"},
            {"id": "alpha-b", "dir": "alpha/answerability/run-b"}]
    (run).mkdir(parents=True)
    (run / "manifest.json").write_text(json.dumps({"repos": repos, "jobs": jobs}))
    (run / "summary.md").write_text(SUMMARY)
    for slug, secs, code in (("alpha", 750, 0), ("beta", 90, 1)):
        d = run / slug / "facet"
        d.mkdir(parents=True)
        (d / "meta.txt").write_text(f"exit_code={code}\nseconds={secs}\n")
        (d / "command.txt").write_text("bin/pi --print --provider prov --model mod-1 -- <prompt.txt>\n")
        (d / "stderr.txt").write_text("boom happened.\n" if code else "")
    a = run / "alpha" / "answerability"
    for r, code, report in (("run-a", 0, "```yaml\nevaluation: x\nchecks: []\n```\n"),
                            ("run-b", 1, "```yaml\nbad: [unclosed\n```\n")):
        (a / r).mkdir(parents=True)
        (a / r / "meta.txt").write_text(f"exit_code={code}\nseconds=10\n")
        (a / r / "report.md").write_text(report)
    (a / "score.md").write_text(SCORE)
    (run / "beta" / "skipped-answerability.md").write_text("# Answerability skipped\n")
    return run


def test_synthetic_run_converts_without_guessing():
    with tempfile.TemporaryDirectory() as t:
        run = make_run(Path(t))
        data, warnings = frh.convert(run)
        repos = {r["name"]: r for r in data["repositories"]}
        assert list(repos) == ["ALPHA", "Beta"]                      # abbreviation from "(ALPHA)"
        assert repos["ALPHA"]["verdicts"] == "P ? B"                  # report-missing -> "?"
        assert repos["ALPHA"]["minutes"] == 12 and repos["Beta"]["minutes"] == 2
        assert repos["Beta"]["verdicts"] == {"reachable-fetch": "A", "brand-new-check": "~"}
        assert any("maybe" in w for w in warnings)                    # unknown verdict left out
        assert [c["id"] for c in data["categories"]] == ["reachable", "callable"]
        assert data["checks"][2]["label"] == "brand-new-check"         # unknown id shown as-is
        assert [q["grade"] for q in repos["ALPHA"]["questions"]] == ["match", "miss", "no-answer"]
        assert "questions" not in repos["Beta"]
        assert [g["id"] for g in data["question_grades"]] == ["match", "miss", "no-answer"]
        assert data["summary_cards"][1]["value"] == "2 of 4"          # 2 of 4 jobs exited 0
        assert data["report"]["footer"].endswith("prov / mod-1")
        assert "2 January 2026, 03:04 UTC" in data["report"]["subtitle"]
        assert "Beta facet exited 1 (stderr: boom happened)" in data["sections"]["verdict_mix"]["footnote"]
        notes = " ".join(data["sections"]["competency"]["notes"])
        assert "did not parse (AL-3)" in notes
        assert "q.alpha.example.org" in notes
        # and it builds
        y = Path(t) / "d.yaml"
        y.write_text(frh.dump(data, warnings, run))
        pdf = build.build(y, Path(t) / "r.pdf")
        assert pdf.stat().st_size > 5000


def test_missing_summary_is_a_warning_not_a_crash():
    with tempfile.TemporaryDirectory() as t:
        run = make_run(Path(t))
        (run / "summary.md").unlink()
        data, warnings = frh.convert(run)
        assert any("summary.md is missing" in w for w in warnings)
        assert data["checks"] == []


def _real_run():
    cand = [os.environ.get("REPO_HERD_RUN"),
            str(ROOT.parent / "repo_herd" / "repo_herd" / "runs" / "20261117T020206Z")]
    for c in cand:
        if c and Path(c, "manifest.json").is_file():
            return Path(c)
    return None


def test_real_run_matches_visual_report_numbers():
    run = _real_run()
    if run is None:
        try:
            import pytest
            pytest.skip("no repo_herd run folder available")
        except ImportError:
            return
    data, warnings = frh.convert(run)
    assert warnings == []
    ref = yaml.safe_load((ROOT / "data" / "example.yaml").read_text())   # transcribed from the PDF
    got = data["repositories"]
    assert len(got) == len(ref["repositories"]) == 12
    for g, r in zip(got, ref["repositories"]):
        assert g["verdicts"] == r["verdicts"], g["name"]
        assert g["minutes"] == r["minutes"], g["name"]
        assert g.get("questions") == r.get("questions"), g["name"]
    assert [c["label"] for c in data["checks"]] == [c["label"] for c in ref["checks"]]
    assert data["summary_cards"][1]["value"] == "22 of 23"


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
