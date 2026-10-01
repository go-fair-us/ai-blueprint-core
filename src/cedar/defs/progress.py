"""Optional timestamped progress lines on stdout."""
from __future__ import annotations

import sys
import time

_enabled = False
_t0 = 0.0


def enable() -> None:
    global _enabled, _t0
    _enabled = True
    _t0 = time.monotonic()
    say("debug on")


def enabled() -> bool:
    return _enabled


def say(msg: str) -> None:
    if not _enabled:
        return
    elapsed = time.monotonic() - _t0
    print(f"[cedar {elapsed:6.1f}s] {msg}", flush=True, file=sys.stdout)
