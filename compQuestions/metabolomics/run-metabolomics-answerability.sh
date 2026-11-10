#!/usr/bin/env bash
# Run Metabolomics Workbench answerability Runs A–D as separate Pi processes.
#
# Each process gets one fenced YAML block and a fresh 15-request budget.
# The answer key is not in the prompt. Reports land under compQuestions/runs/
# (gitignored). score.md is the deterministic grade. llm-grade.md is a
# separate prompt you can paste into a fresh model.
#
# Usage:
#   compQuestions/metabolomics/run-metabolomics-answerability.sh
#   compQuestions/metabolomics/run-metabolomics-answerability.sh --dry-run
#   compQuestions/metabolomics/run-metabolomics-answerability.sh --runs A,B -- --model sonnet
#   compQuestions/metabolomics/run-metabolomics-answerability.sh --grade-only compQuestions/runs/metabolomics-workbench/<stamp>
#
# Pi options (--model, --thinking, --provider) go after --.
# Needs a Pi provider key in the environment or an existing Pi login.
# Does not start the Blueprint knowledge server.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LIB="$ROOT/compQuestions/metabolomics/mw_answerability.py"
SOURCE="$ROOT/compQuestions/metabolomics/metabolomics-workbench-competency-questions-final.md"
PI="$ROOT/bin/pi"

RUNS=(A B C D)
OUT=""
DRY=0
GRADE_ONLY=""
TIMEOUT=1200
SANDBOX=1
PI_EXTRA=()

usage() {
  sed -n '2,20p' "$0"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --out)
      OUT="${2:-}"
      shift 2
      ;;
    --runs)
      IFS=',' read -r -a RUNS <<< "${2:-}"
      shift 2
      ;;
    --dry-run)
      DRY=1
      shift
      ;;
    --grade-only)
      GRADE_ONLY="${2:-}"
      shift 2
      ;;
    --timeout)
      TIMEOUT="${2:-}"
      shift 2
      ;;
    --no-sandbox)
      SANDBOX=0
      shift
      ;;
    --help | -h)
      usage
      exit 0
      ;;
    --)
      shift
      PI_EXTRA=("$@")
      break
      ;;
    *)
      echo "Unknown argument: $1" >&2
      echo "Put Pi options after --, for example: -- --model sonnet" >&2
      exit 2
      ;;
  esac
done

if [[ -n "$GRADE_ONLY" ]]; then
  python3 "$LIB" grade --out "$GRADE_ONLY"
  exit 0
fi

if [[ -z "$OUT" ]]; then
  STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
  OUT="$ROOT/compQuestions/runs/metabolomics-workbench/$STAMP"
fi
mkdir -p "$OUT"

python3 "$LIB" prepare --source "$SOURCE" --out "$OUT" --runs "$(IFS=,; echo "${RUNS[*]}")"

GUARD="This is a competency-answerability run. Fetch with curl so the status line, response headers, and unmodified body are visible. You may use codemode to run those curls and reduce the results. Do not read, grep, or search files in this workspace. Do not open competency-question notes or any answer key. Answer only from responses fetched in this run. Stay on the repository host named in the prompt."

# Hide the question file and this output directory from the agent's bash tool.
# The key and earlier reports live there. Credentials in the home directory stay visible.
sandbox_prefix=()
if [[ "$SANDBOX" -eq 1 ]]; then
  if ! command -v bwrap >/dev/null 2>&1; then
    echo "bwrap is not installed. Re-run with --no-sandbox if you accept that bash can read the answer key." >&2
    exit 1
  fi
  sandbox_prefix=(bwrap --dev-bind / / --die-with-parent --tmpfs "$ROOT/compQuestions")
  case "$OUT" in
    "$ROOT/compQuestions"/*) ;;
    *)
      sandbox_prefix+=(--tmpfs "$OUT")
      ;;
  esac
  sandbox_prefix+=(--)
fi

echo "Output: $OUT" >&2

any_fail=0
for run in "${RUNS[@]}"; do
  run_lc="$(printf '%s' "$run" | tr '[:upper:]' '[:lower:]')"
  run_dir="$OUT/run-$run_lc"
  message="$(python3 "$LIB" message --yaml "$run_dir/input.yaml")"
  {
    printf 'pi'
    printf ' --print --no-session --no-mcp --no-approve --no-context-files --tools bash,codemode'
    printf ' --append-system-prompt %q' "$GUARD"
    for extra in "${PI_EXTRA[@]}"; do
      printf ' %q' "$extra"
    done
    printf ' -- <prompt.txt>\n'
  } > "$run_dir/command.txt"

  if [[ "$DRY" -eq 1 ]]; then
    echo "Run $run: dry-run, prompt in $run_dir/prompt.txt" >&2
    continue
  fi

  echo "Run $run: starting (timeout ${TIMEOUT}s)" >&2
  start=$(date +%s)
  set +e
  if [[ ${#sandbox_prefix[@]} -gt 0 ]]; then
    "${sandbox_prefix[@]}" \
      timeout --foreground "$TIMEOUT" \
      "$PI" \
      --print \
      --no-session \
      --no-mcp \
      --no-approve \
      --no-context-files \
      --tools bash,codemode \
      --append-system-prompt "$GUARD" \
      "${PI_EXTRA[@]}" \
      -- \
      "$message" \
      > "$run_dir/report.md" \
      2> "$run_dir/stderr.txt"
  else
    timeout --foreground "$TIMEOUT" \
      "$PI" \
      --print \
      --no-session \
      --no-mcp \
      --no-approve \
      --no-context-files \
      --tools bash,codemode \
      --append-system-prompt "$GUARD" \
      "${PI_EXTRA[@]}" \
      -- \
      "$message" \
      > "$run_dir/report.md" \
      2> "$run_dir/stderr.txt"
  fi
  code=$?
  set -e
  end=$(date +%s)
  {
    echo "exit_code=$code"
    echo "seconds=$((end - start))"
    echo "timeout=$TIMEOUT"
  } > "$run_dir/meta.txt"
  if [[ "$code" -ne 0 ]]; then
    any_fail=1
    echo "Run $run: exit $code (see $run_dir/stderr.txt)" >&2
  else
    echo "Run $run: saved $run_dir/report.md" >&2
  fi
done

if [[ "$DRY" -eq 1 ]]; then
  echo "Dry run only. No reports to grade." >&2
  exit 0
fi

python3 "$LIB" grade --out "$OUT" >&2
echo "Score: $OUT/score.md" >&2
echo "LLM grade prompt: $OUT/llm-grade.md" >&2
exit "$any_fail"
