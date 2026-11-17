import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from conftest import REAL_RUN, ROOT
from synth import small_run

from impactlib import assess, backends, combine, config, extractors, gaps, review, rubric
from impactlib.runfiles import load_run

needs_real = pytest.mark.skipif(not REAL_RUN.is_dir(), reason="20261117 run not available")


class FakeBackend:
    """Test double: scripted answers (dicts or raw strings), one per call."""
    name = "fake"
    placeholder = False
    model = "fake-model"
    label = "fake / fake-model"

    def __init__(self, answers):
        self.answers = list(answers)
        self.calls = 0

    def complete(self, system, user, gaps_):
        self.calls += 1
        a = self.answers.pop(0) if len(self.answers) > 1 else self.answers[0]
        if callable(a):
            a = a(gaps_)
        return a if isinstance(a, str) else json.dumps(a)


def good(gaps_, x=0.1, y=0.2, why="Evidence names the missing file."):
    return {"placements": [{"gap_id": g["id"], "fix_label": f"Fix {g['key']}"[:40], "x": x, "y": y,
                            "rationale": why, "confidence": "medium"} for g in gaps_]}


def cfg_():
    return config.load()


def run_cli(*args):
    return subprocess.run([sys.executable, str(ROOT / "impact.py"), *args],
                          capture_output=True, text=True)


# ------------------------------------------------------------------ extract
@needs_real
def test_extract_real_run_counts():
    run = load_run(REAL_RUN)
    total = 0
    for repo in run.repos:
        d = gaps.extract_repo(run, repo, cfg_())
        absent = sum(1 for r in repo.rows if r["verdict"] == "absent")
        assert len(d["gaps"]) == absent
        assert all(g["verdict"] == "absent" for g in d["gaps"])
        assert len(d["gaps"]) + sum(d["non_gaps"].values()) == len(repo.rows) == 19
        assert all(g["operator_fix"] and g["evidence"] for g in d["gaps"])
        total += len(d["gaps"])
    assert total == 99
    acdn = gaps.extract_repo(run, run.repos[0], cfg_())
    assert acdn["non_gaps"] == {"present": 1, "partial": 5, "not-observable": 3, "unparsed": 1}


def test_extract_synthetic(tmp_path):
    run = load_run(small_run(tmp_path))
    out = {r.slug: gaps.extract_repo(run, r, cfg_()) for r in run.repos}
    a = out["alpha"]
    assert [g["key"] for g in a["gaps"]] == ["robots-policy", "llms-txt", "openapi-discovery",
                                            "dataset-jsonld", "shacl-shapes", "license-clarity"]
    assert a["non_gaps"] == {"present": 1, "partial": 1, "blocked": 1}  # blocked is not a gap
    shacl = next(g for g in a["gaps"] if g["key"] == "shacl-shapes")
    assert shacl["context"]["block_parsed"] is False
    assert any("did not parse" in n for n in a["sources"]["facet-check"]["notes"])
    assert next(g for g in a["gaps"] if g["key"] == "license-clarity")["category"] == "Governed"
    assert out["beta"]["gaps"] == [] and out["beta"]["non_gaps"] == {"present": 9}
    assert out["gamma"]["sources"]["facet-check"]["available"] is False
    assert run.repos[0].display == "ALP"


def test_gap_verdicts_configurable(tmp_path):
    run = load_run(small_run(tmp_path))
    c = cfg_(); c["gap_verdicts"] = {"facet-check": ["absent", "partial"]}
    d = gaps.extract_repo(run, run.repos[0], c)
    assert "sitemap" in [g["key"] for g in d["gaps"]]


# ------------------------------------------------------------------ validate / assess
def test_validate():
    ids = ["s:a", "s:b"]
    ok = {"placements": [{"gap_id": i, "fix_label": "Do it", "x": 0, "y": 1, "rationale": "r",
                          "confidence": "high"} for i in ids]}
    assert assess.validate(ok, ids) == []
    bad = json.loads(json.dumps(ok)); bad["placements"].append(dict(bad["placements"][0], gap_id="s:new"))
    assert any("not in the gap list" in e for e in assess.validate(bad, ids))
    bad = json.loads(json.dumps(ok)); bad["placements"].pop()
    assert any("missing" in e for e in assess.validate(bad, ids))
    bad = json.loads(json.dumps(ok)); bad["placements"][0]["x"] = 1.5
    assert any("outside" in e for e in assess.validate(bad, ids))
    bad = json.loads(json.dumps(ok)); bad["placements"][0]["fix_label"] = "x" * 41
    assert any("max 40" in e for e in assess.validate(bad, ids))
    bad = json.loads(json.dumps(ok)); bad["placements"][0]["confidence"] = "sure"
    assert assess.validate(bad, ids)
    assert assess.parse_json("Sure!\n```json\n{\"placements\": []}\n```") == {"placements": []}


def _gapfile(tmp_path, slug="alpha"):
    run = load_run(small_run(tmp_path))
    repo = next(r for r in run.repos if r.slug == slug)
    return run, gaps.extract_repo(run, repo, cfg_())


def test_clip_text_ends_on_a_word_or_hard_cuts():
    label = "Publish OpenAPI 3.1 doc for the data API now"  # 44 chars; next char after 40 is a space
    assert len(label) == 44 and assess.clip_text(label, 40) == label[:40]
    mid = "Publish OpenAPI 3.1 doc for the data APIs"  # 41; cut falls inside the last word
    assert len(mid) == 41
    assert assess.clip_text(mid, 40) == "Publish OpenAPI 3.1 doc for the data"
    assert assess.clip_text("y" * 215, 200) == "y" * 200
    rationale = ("The sitemap is absent and robots.txt names no Sitemap line, so this is one "
                 "static file and a few hours of work, but records are already reachable so the "
                 "gain is discovery speed rather than removing a blocker for agents today extra")
    clipped = assess.clip_text(rationale, 200)
    assert len(rationale) > 200 and len(clipped) <= 200 and clipped == clipped.rstrip()
    assert rationale.startswith(clipped) and not clipped.endswith("extra")


def test_overlong_fields_are_clipped_and_accepted(tmp_path):
    run, gf = _gapfile(tmp_path)
    def long(gaps_):
        ans = good(gaps_)
        ans["placements"][0]["fix_label"] = "Publish OpenAPI 3.1 doc for the data API now"
        ans["placements"][1]["rationale"] = "Evidence. " + ("detail " * 40)
        return ans
    logs = []
    be = FakeBackend([long])
    res = assess.assess_repo(gf, be, rubric.load(ROOT / "rubric.md"), cfg_(), tmp_path / "w", 1, {},
                             log=logs.append)
    assert be.calls == 1 and res["attempts"] == [1] and res["clipped"] == [2]
    assert all(len(p["fix_label"]) <= 40 and len(p["rationale"]) <= 200 for p in res["placements"])
    assert res["placements"][0]["fix_label"] == "Publish OpenAPI 3.1 doc for the data API"
    assert any("clipped 1 fix_label and 1 rationale" in m for m in logs)
    cached = list((tmp_path / "w" / "cache").glob("*.json"))
    assert len(cached) == 1
    saved = json.loads(cached[0].read_text())
    assert assess.validate({"placements": saved["placements"]}, [g["id"] for g in gf["gaps"]]) == []


def test_length_clip_does_not_hide_other_errors(tmp_path):
    run, gf = _gapfile(tmp_path)
    def bad(gaps_):
        ans = good(gaps_)
        ans["placements"][0]["fix_label"] = "x" * 44
        ans["placements"][0]["x"] = 2
        return ans
    be = FakeBackend([bad, good])
    res = assess.assess_repo(gf, be, rubric.load(ROOT / "rubric.md"), cfg_(), tmp_path / "w", 1, {},
                             log=lambda m: None)
    assert be.calls == 2 and res["attempts"] == [2]
    assert res["placements"][0]["x"] == 0.1
    assert res["placements"][0]["fix_label"].startswith("Fix ")


def test_retry_on_invalid_then_valid(tmp_path):
    run, gf = _gapfile(tmp_path)
    be = FakeBackend(["not json at all", lambda g: {"placements": []}, good])
    rub = rubric.load(ROOT / "rubric.md")
    res = assess.assess_repo(gf, be, rub, cfg_(), tmp_path / "w", 1, {}, log=lambda m: None)
    assert be.calls == 3 and res["attempts"] == [3]
    assert len(res["placements"]) == len(gf["gaps"])


def test_gives_up_after_max_attempts(tmp_path):
    run, gf = _gapfile(tmp_path)
    be = FakeBackend(["{}"])
    with pytest.raises(SystemExit):
        assess.assess_repo(gf, be, rubric.load(ROOT / "rubric.md"), cfg_(), tmp_path / "w", 1, {},
                           log=lambda m: None)


def test_samples_median_and_variance_and_cache(tmp_path):
    run, gf = _gapfile(tmp_path)
    be = FakeBackend([lambda g: good(g, x=-0.8), lambda g: good(g, x=0.0), lambda g: good(g, x=0.6)])
    rub = rubric.load(ROOT / "rubric.md")
    w = tmp_path / "w"
    res = assess.assess_repo(gf, be, rub, cfg_(), w, 3, {}, log=lambda m: None)
    p = res["placements"][0]
    assert p["x"] == 0.0 and p["high_variance"] is True and len(p["samples"]) == 3
    be2 = FakeBackend([lambda g: good(g, x=0.9)])
    res2 = assess.assess_repo(gf, be2, rub, cfg_(), w, 3, {}, log=lambda m: None)
    assert be2.calls == 0 and res2["cache_hits"] == 3 and res2["placements"][0]["x"] == 0.0


def test_prompt_contains_rubric_and_only_listed_gaps(tmp_path):
    run, gf = _gapfile(tmp_path)
    rub = rubric.load(ROOT / "rubric.md")
    prompt = assess.build_prompt(gf, rub.text, {"verdicts": {"sitemap": "partial"}})
    assert "effort to implement" in prompt and "facet-check:llms-txt" in prompt
    assert "facet-check:sitemap" not in prompt   # partial is context, not a gap


def test_stub_is_labelled_placeholder(tmp_path):
    run, gf = _gapfile(tmp_path)
    be = backends.make("stub", cfg_())
    res = assess.assess_repo(gf, be, rubric.load(ROOT / "rubric.md"), cfg_(), tmp_path / "w", 1, {},
                             log=lambda m: None)
    assert res["placeholder"] is True
    assert all("PLACEHOLDER" in p["rationale"] for p in res["placements"])


def test_pi_backend_missing_binary_is_a_clear_error():
    c = cfg_(); c["pi"]["bin"] = "/nonexistent/pi"
    with pytest.raises(SystemExit, match="not found"):
        backends.make("pi", c)


# ------------------------------------------------------------------ review / overrides
def _all(tmp_path, *extra):
    runp = small_run(tmp_path / "runs")
    work = tmp_path / "work"
    r = run_cli("all", "--run", str(runp), "--work", str(work), "--backend", "stub",
                "-o", str(tmp_path / "out.pdf"), *extra)
    assert r.returncode == 0, r.stderr
    return runp, work


def test_hand_edits_survive_rerun(tmp_path):
    runp, work = _all(tmp_path)
    pf = work / "placements" / "alpha.yaml"
    doc = yaml.safe_load(pf.read_text())
    assert doc["placeholder"] is True and "PLACEHOLDER" in doc["warning"]
    llms = next(p for p in doc["points"] if p["gap_id"] == "facet-check:llms-txt")
    llms["x"], llms["label"] = 0.42, "My label"
    doc["points"] = [p for p in doc["points"] if p["gap_id"] != "facet-check:robots-policy"]
    pf.write_text(yaml.safe_dump(doc, sort_keys=False))
    r = run_cli("review", "--run", str(runp), "--work", str(work))
    assert r.returncode == 0, r.stderr
    ov = yaml.safe_load((work / "overrides.yaml").read_text())
    assert ov["repos"]["alpha"]["facet-check:llms-txt"] == {"x": 0.42, "label": "My label"}
    assert ov["repos"]["alpha"]["facet-check:robots-policy"] == {"hide": True}
    # a full re-run keeps the edits
    r = run_cli("all", "--run", str(runp), "--work", str(work), "--backend", "stub",
                "-o", str(tmp_path / "out2.pdf"))
    assert r.returncode == 0, r.stderr
    doc = yaml.safe_load(pf.read_text())
    llms = next(p for p in doc["points"] if p["gap_id"] == "facet-check:llms-txt")
    assert llms["x"] == 0.42 and llms["label"] == "My label" and llms["quadrant"] == "Big bets"
    assert not any(p["gap_id"] == "facet-check:robots-policy" for p in doc["points"])


def test_placements_plot_standalone(tmp_path):
    runp, work = _all(tmp_path)
    out = tmp_path / "alpha.png"
    r = subprocess.run([sys.executable, str(ROOT / "quadrant_plot.py"),
                        str(work / "placements" / "alpha.yaml"), "-o", str(out)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert out.stat().st_size > 1000


# ------------------------------------------------------------------ combined
def test_combined_groups_by_check(tmp_path):
    runp, work = _all(tmp_path)
    run = load_run(runp)
    gfs = gaps.load_gaps(work, [r.slug for r in run.repos])
    pl = review.load_placements(work, [r.slug for r in run.repos])
    comb = combine.combine(gfs, pl, cfg_())
    assert comb["n_repos"] == 3          # gamma has no facet results
    rows = {r["key"]: r for r in comb["rows"]}
    assert rows["llms-txt"]["count"] == 2 and rows["openapi-discovery"]["count"] == 2
    assert rows["mcp-exposure"]["count"] == 1   # blocked in alpha, absent in delta
    assert comb["rows"][0]["count"] == 2
    assert any(p["label"] == "llms.txt (2/3)" for p in comb["points"])


def test_combined_median():
    gfs = [{"repo": {"slug": s, "display": s}, "sources": {"x": {"available": True}},
            "gaps": [{"id": "x:k", "source": "x", "key": "k", "label": "K", "category": "C"}]}
           for s in "abc"]
    pl = {s: {"points": [{"gap_id": "x:k", "x": x, "y": y, "label": "f"}]}
          for s, x, y in (("a", -0.9, 0.1), ("b", 0.1, 0.5), ("c", 0.3, 0.9))}
    comb = combine.combine(gfs, pl, cfg_())
    r = comb["rows"][0]
    assert (r["x"], r["y"], r["count"], r["quadrant"]) == (0.1, 0.5, 3, "Big bets")


# ------------------------------------------------------------------ extension point
def test_custom_extractor_source(tmp_path):
    @extractors.register("competency-question")
    def cq(run, repo, cfg):
        return extractors.ExtractResult(gaps=[{
            "id": "competency-question:Q1", "source": "competency-question", "key": "Q1",
            "label": "Q1 unanswered", "category": "Answerable", "verdict": "miss",
            "evidence_url": "", "evidence": [], "summary": "", "report_gaps": [],
            "operator_fix": "", "context": {}}], non_gaps={"match": 3})
    try:
        run = load_run(small_run(tmp_path))
        c = cfg_(); c["sources"] = ["facet-check", "competency-question"]
        d = gaps.extract_repo(run, run.repos[0], c)
        assert {g["source"] for g in d["gaps"]} == {"facet-check", "competency-question"}
        assert d["non_gaps"]["match"] == 3
    finally:
        extractors.REGISTRY.pop("competency-question")


# ------------------------------------------------------------------ report
def _pdftext(pdf, first=None, last=None):
    args = ["pdftotext", "-layout"]
    if first:
        args += ["-f", str(first), "-l", str(last or first)]
    return subprocess.run(args + [str(pdf), "-"], capture_output=True, text=True).stdout


def test_report_synthetic(tmp_path):
    _all(tmp_path)
    pdf = tmp_path / "out.pdf"
    text = _pdftext(pdf)
    assert "PLACEHOLDER" in _pdftext(pdf, 1)
    assert "nothing to place" in text                 # beta (0 gaps) and gamma (no data)
    assert "Governed" in text                         # fifth category flows through
    pages = int(subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True)
                .stdout.split("Pages:")[1].split()[0])
    assert pages >= 1 + 4 + 1


@needs_real
def test_report_real_run_stub(tmp_path):
    out = tmp_path / "impact.pdf"
    r = run_cli("all", "--run", str(REAL_RUN), "--work", str(tmp_path / "w"), "--backend", "stub",
                "-o", str(out))
    assert r.returncode == 0, r.stderr
    p1 = _pdftext(out, 1)
    assert "99" in p1 and "PLACEHOLDER" in p1 and "MCP exposure" in p1
    assert "10/12" in p1


def test_quadrant_plot_cli_still_works(tmp_path):
    for src, extra in (("example.yaml", []), ("example.csv", ["--config", str(ROOT / "example.yaml")])):
        out = tmp_path / (src + ".png")
        r = subprocess.run([sys.executable, str(ROOT / "quadrant_plot.py"), str(ROOT / src),
                            *extra, "-o", str(out)], capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        assert out.stat().st_size > 10000


def test_gap_files_match_schema(tmp_path):
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads((ROOT / "schema" / "gap-file.schema.json").read_text())
    run = load_run(small_run(tmp_path))
    for repo in run.repos:
        jsonschema.validate(gaps.extract_repo(run, repo, cfg_()), schema)
