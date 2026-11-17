#!/usr/bin/env python3
"""Layout stress check: many repositories, checks and categories, long rationales.

    python3 tests/stress.py /tmp/stress     # writes /tmp/stress/stress.pdf
Placements come from a seeded random test backend (clearly not a model).
"""
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "tests"))
from synth import write_run  # noqa: E402
from impactlib import backends  # noqa: E402
import impact  # noqa: E402

PROPS = ["Be reachable", "Be readable", "Be callable", "Be meaningful", "Be governed"]


class RandomBackend:
    name = "random-test"; placeholder = True; model = "seeded-random"
    label = "seeded random (TEST, not model output)"

    def __init__(self, cfg, model=None, provider=None):
        pass

    def complete(self, system, user, gaps):
        rnd = random.Random(len(user))
        return json.dumps({"placements": [{
            "gap_id": g["id"], "fix_label": ("Publish a much longer fix label " + g["key"])[:40],
            "x": round(rnd.uniform(-0.95, 0.95), 2), "y": round(rnd.uniform(-0.95, 0.95), 2),
            "rationale": ("Synthetic rationale that is deliberately long so the table has to wrap "
                          "over several lines and push rows onto a continuation page. ")[:rnd.randint(60, 200)],
            "confidence": "low"} for g in gaps]})


def main(out: Path):
    out.mkdir(parents=True, exist_ok=True)
    checks = [(PROPS[i % 5], f"check-{i:02d}") for i in range(24)]
    rnd = random.Random(7)
    repos = [{"name": f"Repository number {i} (R{i})", "slug": f"r{i}",
              "verdicts": {ev: rnd.choice(["absent", "absent", "present", "partial", "blocked"])
                           for _, ev in checks}} for i in range(20)]
    repos[3]["verdicts"] = {ev: "present" for _, ev in checks}
    repos[4]["verdicts"] = {ev: "absent" for _, ev in checks}
    run = write_run(out / "runs", repos, checks=checks)
    backends.BACKENDS["random-test"] = RandomBackend
    impact.main(["extract", "--run", str(run), "--work", str(out / "work")])
    import impactlib.assess as A
    cfg = impact.config.load()
    from impactlib import gaps, rubric
    be = RandomBackend(cfg)
    rub = rubric.load(cfg["rubric"])
    (out / "work" / "assess").mkdir(exist_ok=True)
    for gf in gaps.load_gaps(out / "work", [r["slug"] for r in repos]):
        res = A.assess_repo(gf, be, rub, cfg, out / "work", 1, {}, log=lambda m: None)
        (out / "work" / "assess" / f"{gf['repo']['slug']}.json").write_text(json.dumps(res))
    impact.main(["review", "--run", str(run), "--work", str(out / "work")])
    impact.main(["report", "--run", str(run), "--work", str(out / "work"), "-o", str(out / "stress.pdf")])


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/stress"))
