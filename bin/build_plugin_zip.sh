#!/usr/bin/env bash
# Build the niaid-blueprint agent plugin release archive.
#
#   ./bin/build_plugin_zip.sh [REF] [OUT]
#
# REF defaults to HEAD; OUT defaults to dist/niaid-blueprint.zip. The archive holds
# the committed contents of niaid-blueprint/ (tracked files only, so __pycache__ and
# other ignored files never ship) under a top-level niaid-blueprint/ folder. The
# catalog files (catalog.yaml, ard.json) describe the plugin and are left out.
# The GitHub Actions release workflow runs this same script.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REF="${1:-HEAD}"
OUT="${2:-$ROOT/dist/niaid-blueprint.zip}"

cd "$ROOT"
mkdir -p "$(dirname "$OUT")"
git archive --format=zip --prefix=niaid-blueprint/ -o "$OUT" "$REF:niaid-blueprint" -- \
  . ':(exclude)catalog.yaml' ':(exclude)ard.json'

version="$(git show "$REF:niaid-blueprint/plugin.json" | python3 -c 'import json,sys; print(json.load(sys.stdin)["version"])')"
echo "wrote $OUT (niaid-blueprint $version from $REF)"
