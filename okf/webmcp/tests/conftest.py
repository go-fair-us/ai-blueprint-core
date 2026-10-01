"""Put the webmcp package and okf_core on sys.path for tests."""

from __future__ import annotations

import sys
from pathlib import Path

WEB_ROOT = Path(__file__).resolve().parent.parent
OKF_ROOT = WEB_ROOT.parent
REPO_ROOT = OKF_ROOT.parent
OKF_CORE_SRC = REPO_ROOT / "src" / "okf_core" / "src"

for path in (WEB_ROOT, OKF_CORE_SRC):
    text = str(path)
    if path.is_dir() and text not in sys.path:
        sys.path.insert(0, text)
