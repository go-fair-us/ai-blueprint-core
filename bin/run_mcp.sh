#!/usr/bin/env bash
# Start the Blueprint MCP server from the repo root, regardless of the
# caller's current directory. This script lives in bin/; content paths
# resolve from the parent tree.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is not on PATH. Install uv, then run ./bin/run_mcp.sh" >&2
  exit 1
fi

exec uv run --extra mcp python -m mcp_bp.server
