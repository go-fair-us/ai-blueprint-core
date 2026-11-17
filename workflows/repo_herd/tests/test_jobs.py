"""Planner and grader tests for the repository herd. No network and no Pi."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import jobs

ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "workflows" / "repo_herd"
CSV = ROOT / "docs" / "NIAID_RepostoryList.csv"
QUESTIONS = ROOT / "compQuestions" / "answerability_runs.md"


def prepare(out: Path, repos: str = "", only: str = "all") -> dict:
    return jobs.prepare(
        csv_path=CSV,
        questions_path=QUESTIONS,
        aliases_path=HERE / "aliases.json",
        template_path=HERE / "facet-prompt.md",
        out=out,
        repos_filter=repos,
        only=only,
    )


def test_full_catalog_shapes(tmp_path: Path) -> None:
    manifest = prepare(tmp_path / "stamp")
    facet = [job for job in manifest["jobs"] if job["kind"] == "facet"]
    answer = [job for job in manifest["jobs"] if job["kind"] == "answerability"]
    assert len(facet) == 12
    assert len(answer) == 11
    assert manifest["warnings"] == []

    skipped_names = set()
    for repo in manifest["repos"]:
        skipped = tmp_path / "stamp" / repo["slug"] / "skipped-answerability.md"
        if skipped.is_file():
            skipped_names.add(repo["name"])
    assert skipped_names == {
        "MACS WHIS Combined Cohort Study (MWCCS)",
        "ACTG",
        "ITN Trialshare",
        "immunspace",
        "CEIRR",
        "ClinEpiDB",
    }

    prompts = list((tmp_path / "stamp").rglob("prompt.txt"))
    blob = "\n".join(path.read_text(encoding="utf-8") for path in prompts)
    assert "IMPACC" not in blob
    assert "Natural History Study" not in blob
    assert "SDY1760" not in blob
    assert "| ID | Expected answer |" not in blob


def test_immunspace_origin_and_hint(tmp_path: Path) -> None:
    manifest = prepare(tmp_path / "stamp", repos="immunspace")
    repo = manifest["repos"][0]
    assert repo["origin"] == "https://immunespace.org/"
    assert repo["host"] == "immunespace.org"
    assert "https://immunespace.org/query/filters" in repo["hints"]
    prompt = (tmp_path / "stamp" / repo["slug"] / "facet" / "prompt.txt").read_text(encoding="utf-8")
    assert "https://immunespace.org/" in prompt
    assert "https://immunespace.org/query/filters" in prompt
    assert repo["notes"] not in prompt
    assert "ST000001" not in prompt


def test_veupathdb_alias_keeps_the_answer_key_out(tmp_path: Path) -> None:
    manifest = prepare(tmp_path / "stamp", repos="veupath")
    repo = manifest["repos"][0]
    assert repo["origin"] == "https://veupathdb.org/"
    assert repo["question_origin"] == "https://plasmodb.org/"
    facet = (tmp_path / "stamp" / repo["slug"] / "facet" / "prompt.txt").read_text(encoding="utf-8")
    assert "https://veupathdb.org/" in facet
    assert "There is no prior compatibility note" in facet

    run_a = tmp_path / "stamp" / repo["slug"] / "answerability" / "run-a"
    prompt = (run_a / "prompt.txt").read_text(encoding="utf-8")
    yaml_text = (run_a / "input.yaml").read_text(encoding="utf-8")
    key = (run_a / "key.md").read_text(encoding="utf-8")
    assert prompt.startswith("/competency-answerability https://plasmodb.org/ ")
    assert "GenesByTaxonGene" not in prompt
    assert "apical membrane antigen 1" not in prompt
    questions = jobs.yaml.safe_load(yaml_text)["questions"]
    assert any("Is 'gene' a record type" in question for question in questions)
    assert "GenesByTaxonGene" in key
    args = jobs.parse_pi_args(prompt.removeprefix("/competency-answerability "), honor_backslash=True)
    assert args[0] == "https://plasmodb.org/"
    assert args[1] == yaml_text


def test_every_answerability_message_roundtrips(tmp_path: Path) -> None:
    prepare(tmp_path / "stamp")
    for prompt_path in (tmp_path / "stamp").rglob("answerability/**/prompt.txt"):
        prompt = prompt_path.read_text(encoding="utf-8")
        yaml_text = (prompt_path.parent / "input.yaml").read_text(encoding="utf-8")
        for honor in (True, False):
            args = jobs.parse_pi_args(
                prompt.removeprefix("/competency-answerability "),
                honor_backslash=honor,
            )
            assert len(args) == 2
            assert args[1] == yaml_text
        assert "| ID | Expected answer |" not in prompt


def test_tb_portals_hints_and_single_run(tmp_path: Path) -> None:
    manifest = prepare(tmp_path / "stamp", repos="tb portals")
    repo = manifest["repos"][0]
    assert "https://datasharing.tbportals.niaid.nih.gov/#/data-api" in repo["hints"]
    runs = [job for job in manifest["jobs"] if job["kind"] == "answerability"]
    assert [job["run"] for job in runs] == ["A"]
    prompt = (tmp_path / "stamp" / repo["slug"] / "facet" / "prompt.txt").read_text(encoding="utf-8")
    assert "token based" not in prompt
    assert "evals/reachable-fetch.md" in prompt
    assert "evals/competency-questions.md" in prompt


def test_repo_filter_and_only(tmp_path: Path) -> None:
    manifest = prepare(tmp_path / "stamp", repos="immport,iedb", only="answerability")
    assert {repo["name"] for repo in manifest["repos"]} == {"ImmPort", "IEDB"}
    assert all(job["kind"] == "answerability" for job in manifest["jobs"])
    assert len(manifest["jobs"]) == 4


def test_metabolomics_prior_note(tmp_path: Path) -> None:
    csv_path = tmp_path / "one.csv"
    csv_path.write_text(
        "Community,Name,URL,Additional Reference URL,style,open web search,NDE,GDS,Notes\n"
        "X,Metabolomics Workbench,https://www.metabolomicsworkbench.org/,https://www.metabolomicsworkbench.org/tools/mw_rest.php,REST,,secret note,,\n",
        encoding="utf-8",
    )
    jobs.prepare(
        csv_path=csv_path,
        questions_path=QUESTIONS,
        aliases_path=HERE / "aliases.json",
        template_path=HERE / "facet-prompt.md",
        out=tmp_path / "out",
    )
    prompt = next((tmp_path / "out").rglob("facet/prompt.txt")).read_text(encoding="utf-8")
    assert "MW_REST_API_NIAID_Blueprint_Compatibility.md" in prompt
    assert "secret note" not in prompt
    assert "www.metabolomicsworkbench.org" in prompt


def test_grade_rules() -> None:
    assert jobs.grade_check("contains: 'NCT05559099'", "NCT05559099", "The id is NCT05559099.") == "match"
    assert jobs.grade_check("contains: 'Monkeypox' AND '2022-10-10'", "Monkeypox; 2022-10-10", "nope") == "miss"
    assert jobs.grade_check("numeric, tolerance: may grow; accept >=13", "13", "20 studies") == "match"
    assert jobs.grade_check("numeric, tolerance: may grow; accept >=13", "13", "4") == "miss"
    assert jobs.grade_check("exact (case-insensitive)", "Belarus", "Belarus") == "ungraded"
    assert jobs.grade_check("exact on 58560", "58560 (IEDB_EPITOPE:58560)", "structure 58560") == "match"
    assert jobs.grade_check("exact on branch_or_tag", "v5.0.4", "v5.0.4") == "ungraded"
    assert jobs.grade_check("exact 'GenesByTaxonGene'", "Yes; GenesByTaxonGene", "Yes; GenesByTaxonGene") == "match"
    assert jobs.grade_check("contains: '401' or 'no' AND 'Study Search'", "No", "401") == "ungraded"
    assert jobs.grade_check("contains: 'Bearer'", "Bearer", None) == "no-answer"


def test_finish_extracts_facet_yaml_and_scores_answers(tmp_path: Path) -> None:
    manifest = prepare(tmp_path / "stamp", repos="immport")
    repo = manifest["repos"][0]
    slug = repo["slug"]
    report = tmp_path / "stamp" / slug / "facet" / "report.md"
    report.write_text(
        """```yaml
evaluation: reachable-fetch
target: https://www.immport.org/
verdict: present
checks:
  - id: homepage-get
    result: pass
    evidence: "GET https://www.immport.org/ returned HTTP 200"
fetches:
  - url: https://www.immport.org/
    method: GET
    status: 200
```

```yaml
evaluation: robots-policy
target: https://www.immport.org/robots.txt
verdict: partial
checks:
  - id: robots
    result: pass
    evidence: "https://www.immport.org/robots.txt HTTP 200"
```
""",
        encoding="utf-8",
    )
    run_a = tmp_path / "stamp" / slug / "answerability" / "run-a"
    (run_a / "report.md").write_text(
        """```yaml
evaluation: competency-answerability
verdict: partial
checks:
  - id: q1
    answer: "159 and NCT00078195"
    result: pass
  - id: q2
    answer: "someone else"
    result: fail
  - id: q3
    answer: "SNOMED 248152002"
    result: pass
```
""",
        encoding="utf-8",
    )
    (run_a / "meta.txt").write_text("exit_code=0\nseconds=3\ntimeout=1200\nkind=answerability\n", encoding="utf-8")

    summary = jobs.finish(tmp_path / "stamp")
    assert "reachable-fetch" in summary
    assert "| 1 | Be reachable | reachable-fetch | present | https://www.immport.org/ |" in summary
    assert "report did not include this evaluation" in summary
    assert "llms-txt" in summary

    score = (tmp_path / "stamp" / slug / "answerability" / "score.md").read_text(encoding="utf-8")
    assert "| IMMPORT-1 | stable | ungraded |" in score
    assert "| IMMPORT-2 | stable | miss |" in score
    assert "| IMMPORT-3 | stable | match |" in score
    run_b = tmp_path / "stamp" / slug / "answerability" / "run-b"
    assert "no-report" in (tmp_path / "stamp" / slug / "answerability" / "score.md").read_text(encoding="utf-8")
    assert (run_b / "key.md").is_file()
