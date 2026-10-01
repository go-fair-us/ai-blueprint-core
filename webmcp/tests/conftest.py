"""Put the webmcp directory on sys.path for tests."""

from __future__ import annotations

import sys
from pathlib import Path

WEB_ROOT = Path(__file__).resolve().parent.parent
text = str(WEB_ROOT)
if text not in sys.path:
    sys.path.insert(0, text)
