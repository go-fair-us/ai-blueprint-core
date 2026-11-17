import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

STAMP = "20261117T020206Z"
_candidates = [os.environ.get("IMPACT_TEST_RUN"),
               ROOT.parent / "repo_herd" / "runs" / STAMP,          # workflows/impactQuadrants
               Path("/workspace/repo_herd/repo_herd/runs") / STAMP]  # Grok Bot box copy
REAL_RUN = next((Path(c) for c in _candidates if c and Path(c).is_dir()), Path("/nonexistent"))
