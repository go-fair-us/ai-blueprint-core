"""Package and template paths."""
from __future__ import annotations

from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
EXAMPLE_PATH = PACKAGE_ROOT / "example.json"
TOOL_IRI = "https://github.com/go-fair-us/ai-blueprint-core#cedar-extract"
DEFAULT_OBSCURA_BIN = Path("/home/fils/src/git/obscura/target/release/obscura")
