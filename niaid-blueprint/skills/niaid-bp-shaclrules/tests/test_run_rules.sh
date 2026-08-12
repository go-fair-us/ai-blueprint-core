#!/usr/bin/env bash
# Smoke: Socrates rule materializes :Mortal.
set -euo pipefail
cd "$(dirname "$0")/.."

out="$(deno run -A scripts/run_rules.ts assets/examples/socrates.srl)"
echo "$out" | grep -q ':Mortal' || {
  echo "FAIL: expected :Mortal in output, got:" >&2
  echo "$out" >&2
  exit 1
}

all="$(deno run -A scripts/run_rules.ts --all assets/examples/socrates.srl)"
echo "$all" | grep -q ':Man' || {
  echo "FAIL: --all should include :Man" >&2
  exit 1
}

deno run -A scripts/run_rules.ts --help >/dev/null

echo "OK: run_rules smoke passed"
