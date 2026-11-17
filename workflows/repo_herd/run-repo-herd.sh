#!/usr/bin/env bash
# Run a facet review and competency-answerability jobs for each repository
# in a CSV, as fresh Pi processes in a Herdr pane pool.
#
# Usage:
#   workflows/repo_herd/run-repo-herd.sh --dry-run
#   workflows/repo_herd/run-repo-herd.sh --repos immport,iedb --concurrency 2
#   workflows/repo_herd/run-repo-herd.sh --only facet
#   workflows/repo_herd/run-repo-herd.sh --only answerability --no-sandbox
#   workflows/repo_herd/run-repo-herd.sh -- --provider openai --model gpt-4o-mini
#
# Default Pi model is --provider nrp --model deepseek-v4-flash.
# Pi options go after --. --provider, --model, or --models there replace that default.
# Facet jobs need the Blueprint knowledge server on 127.0.0.1:8000.
# Start it first with ./bin/run_mcp.sh. This script does not start it.
# Answerability jobs pass --no-mcp.
# A Herdr server must already be running for a live run (`herdr` in another terminal).

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
HERE="$ROOT/workflows/repo_herd"
JOBS="$HERE/jobs.py"
CSV="$ROOT/docs/NIAID_RepostoryList.csv"
QUESTIONS="$ROOT/compQuestions/answerability_runs.md"
ALIASES="$HERE/aliases.json"
TEMPLATE="$HERE/facet-prompt.md"
FACET_SYSTEM="$HERE/facet-system.txt"
ANSWER_SYSTEM="$HERE/answerability-system.txt"

OUT=""
DRY=0
ONLY="all"
REPOS=""
CONCURRENCY=3
FACET_TIMEOUT=2700
ANSWER_TIMEOUT=1200
SANDBOX=1
CLEANUP=0
PI_EXTRA=()

usage() {
  sed -n '2,17p' "$0"
}

log() {
  printf '%s\n' "$*" >&2
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --out)
      OUT="${2:-}"
      shift 2
      ;;
    --csv)
      CSV="${2:-}"
      shift 2
      ;;
    --repos)
      REPOS="${2:-}"
      shift 2
      ;;
    --only)
      ONLY="${2:-}"
      shift 2
      ;;
    --concurrency)
      CONCURRENCY="${2:-}"
      shift 2
      ;;
    --facet-timeout)
      FACET_TIMEOUT="${2:-}"
      shift 2
      ;;
    --answerability-timeout)
      ANSWER_TIMEOUT="${2:-}"
      shift 2
      ;;
    --dry-run)
      DRY=1
      shift
      ;;
    --no-sandbox)
      SANDBOX=0
      shift
      ;;
    --cleanup)
      CLEANUP=1
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
      echo "Put Pi options after --, for example: -- --provider openai --model gpt-4o-mini" >&2
      exit 2
      ;;
  esac
done

if [[ "$CONCURRENCY" -lt 1 ]]; then
  echo "--concurrency must be at least 1" >&2
  exit 2
fi

# Default model. Flags after -- replace this pair when they name a provider or model.
MODEL_ARGS=(--provider nrp --model deepseek-v4-flash)
for arg in "${PI_EXTRA[@]}"; do
  case "$arg" in
    --provider|--provider=*|--model|--model=*|--models|--models=*)
      MODEL_ARGS=()
      break
      ;;
  esac
done

if [[ -z "$OUT" ]]; then
  STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
  OUT="$HERE/runs/$STAMP"
fi
mkdir -p "$OUT"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required to run workflows/repo_herd/jobs.py" >&2
  exit 1
fi
if ! command -v jq >/dev/null 2>&1; then
  echo "jq is required to read manifest.json" >&2
  exit 1
fi

uv run python "$JOBS" prepare \
  --csv "$CSV" \
  --questions "$QUESTIONS" \
  --aliases "$ALIASES" \
  --template "$TEMPLATE" \
  --out "$OUT" \
  --repos "$REPOS" \
  --only "$ONLY"

write_run_sh() {
  local dest="$1" kind="$2" prompt="$3" report="$4" stderr_path="$5" meta="$6" sentinel="$7" timeout="$8"
  local system no_mcp extra_quoted="" model_quoted="" arg
  if [[ "$kind" == "facet" ]]; then
    system="$FACET_SYSTEM"
    no_mcp=""
  else
    system="$ANSWER_SYSTEM"
    no_mcp="--no-mcp"
  fi
  for arg in "${MODEL_ARGS[@]}"; do
    model_quoted+=" $(printf '%q' "$arg")"
  done
  for arg in "${PI_EXTRA[@]}"; do
    extra_quoted+=" $(printf '%q' "$arg")"
  done
  cat >"$dest" <<EOF
#!/usr/bin/env bash
set -u
ROOT=$(printf '%q' "$ROOT")
PROMPT=$(printf '%q' "$prompt")
REPORT=$(printf '%q' "$report")
REPORT_TMP=$(printf '%q' "$report.partial")
STDERR=$(printf '%q' "$stderr_path")
STDERR_TMP=$(printf '%q' "$stderr_path.partial")
META=$(printf '%q' "$meta")
SYSTEM=$(printf '%q' "$system")
SENTINEL=$(printf '%q' "$sentinel")
TIMEOUT=$(printf '%q' "$timeout")
STAMP=$(printf '%q' "$OUT")
SANDBOX=$SANDBOX
NO_MCP=$(printf '%q' "$no_mcp")
MODEL_ARGS=($model_quoted)
PI_EXTRA=($extra_quoted)
start=\$(date +%s)
set +e
if [[ "\$SANDBOX" -eq 1 ]]; then
  bwrap --dev-bind / / --die-with-parent --tmpfs "\$ROOT/compQuestions" --tmpfs "\$STAMP" -- \\
    timeout --foreground "\$TIMEOUT" \\
    "\$ROOT/bin/pi" \\
    --print --no-session --no-approve --no-context-files --tools bash,codemode \\
    \$NO_MCP \\
    --append-system-prompt "\$SYSTEM" \\
    "\${MODEL_ARGS[@]}" \\
    "\${PI_EXTRA[@]}" \\
    -- "\$(cat "\$PROMPT")" \\
    > "\$REPORT_TMP" 2> "\$STDERR_TMP"
else
  timeout --foreground "\$TIMEOUT" \\
    "\$ROOT/bin/pi" \\
    --print --no-session --no-approve --no-context-files --tools bash,codemode \\
    \$NO_MCP \\
    --append-system-prompt "\$SYSTEM" \\
    "\${MODEL_ARGS[@]}" \\
    "\${PI_EXTRA[@]}" \\
    -- "\$(cat "\$PROMPT")" \\
    > "\$REPORT_TMP" 2> "\$STDERR_TMP"
fi
code=\$?
end=\$(date +%s)
mv -f "\$REPORT_TMP" "\$REPORT"
mv -f "\$STDERR_TMP" "\$STDERR"
{
  echo "exit_code=\$code"
  echo "seconds=\$((end - start))"
  echo "timeout=\$TIMEOUT"
  echo "kind=$kind"
} > "\$META"
printf '%s %s\\n' "\$SENTINEL" "\$code"
exit 0
EOF
  chmod +x "$dest"
}

write_job_scripts() {
  local id kind dir prompt timeout sentinel dest
  while IFS=$'\t' read -r id kind dir; do
    prompt="$OUT/${dir}/prompt.txt"
    if [[ "$kind" == "facet" ]]; then
      timeout="$FACET_TIMEOUT"
    else
      timeout="$ANSWER_TIMEOUT"
    fi
    sentinel="REPO_HERD_JOB_${id}_DONE"
    dest="$OUT/${dir}/run.sh"
    write_run_sh "$dest" "$kind" "$prompt" "$OUT/${dir}/report.md" "$OUT/${dir}/stderr.txt" "$OUT/${dir}/meta.txt" "$sentinel" "$timeout"
    {
      printf 'bin/pi --print --no-session --no-approve --no-context-files --tools bash,codemode'
      if [[ "$kind" == "answerability" ]]; then
        printf ' --no-mcp'
      fi
      printf ' --append-system-prompt %q' "$([[ "$kind" == "facet" ]] && printf '%s' "$FACET_SYSTEM" || printf '%s' "$ANSWER_SYSTEM")"
      for arg in "${MODEL_ARGS[@]}" "${PI_EXTRA[@]}"; do
        printf ' %q' "$arg"
      done
      printf ' -- <prompt.txt>\n'
      printf 'timeout_seconds=%s\n' "$timeout"
      printf 'sandbox=%s\n' "$SANDBOX"
      printf 'sentinel=%s\n' "$sentinel"
    } >"$OUT/${dir}/command.txt"
  done < <(jq -r '.jobs[] | [.id, .kind, .dir] | @tsv' "$OUT/manifest.json")
}

if [[ ${#MODEL_ARGS[@]} -gt 0 ]]; then
  log "Pi model: ${MODEL_ARGS[*]}"
else
  log "Pi model: flags after --"
fi
write_job_scripts

if [[ "$DRY" -eq 1 ]]; then
  log "Dry run only. Prompts and run.sh are in $OUT. Herdr and Pi were not started."
  exit 0
fi

for cmd in herdr pi jq; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "$cmd is not on PATH" >&2
    exit 1
  fi
done

if ! herdr agent list >/dev/null 2>&1; then
  echo "Herdr server is not reachable. Start it with: herdr" >&2
  exit 1
fi

facet_jobs="$(jq '[.jobs[] | select(.kind == "facet")] | length' "$OUT/manifest.json")"
if [[ "$facet_jobs" -gt 0 ]]; then
  if ! curl -s -o /dev/null --max-time 3 http://127.0.0.1:8000/mcp; then
    echo "Blueprint MCP server is not listening on 127.0.0.1:8000. Start it with ./bin/run_mcp.sh" >&2
    exit 1
  fi
fi

if [[ "$SANDBOX" -eq 1 ]] && ! command -v bwrap >/dev/null 2>&1; then
  echo "bwrap is not installed. Re-run with --no-sandbox if you accept that bash can read the answer key." >&2
  exit 1
fi

WS_ID=""
cleanup() {
  if [[ "$CLEANUP" -eq 1 && -n "$WS_ID" ]]; then
    herdr workspace close "$WS_ID" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

LABEL="repo-herd-$(date -u +%Y%m%dT%H%M%SZ)"
log "creating workspace $LABEL"
CREATE_JSON="$(herdr workspace create --cwd "$ROOT" --label "$LABEL" --no-focus)"
WS_ID="$(printf '%s' "$CREATE_JSON" | jq -er '.result.workspace.workspace_id')"
ROOT_PANE="$(printf '%s' "$CREATE_JSON" | jq -er '.result.root_pane.pane_id')"
printf '%s\n' "$WS_ID" >"$OUT/workspace_id"
log "workspace_id=$WS_ID"
log "watch with: herdr workspace focus $WS_ID"

PANES=("$ROOT_PANE")
previous="$ROOT_PANE"
direction="right"
while [[ "${#PANES[@]}" -lt "$CONCURRENCY" ]]; do
  split_json="$(herdr pane split "$previous" --direction "$direction" --cwd "$ROOT" --no-focus)"
  previous="$(printf '%s' "$split_json" | jq -er '.result.pane.pane_id')"
  PANES+=("$previous")
  direction="down"
done
printf '%s\n' "${PANES[@]}" >"$OUT/panes.txt"

declare -A JOB_HOST=()
declare -A JOB_DIR=()
declare -A JOB_KIND=()
declare -A BUSY_HOST=()
declare -A PANE_JOB=()
declare -A PANE_START=()
declare -A PANE_STUCK=()
declare -A LAUNCH_FAILS=()
QUEUE=()

while IFS=$'\t' read -r id host dir kind; do
  JOB_HOST["$id"]="$host"
  JOB_DIR["$id"]="$dir"
  JOB_KIND["$id"]="$kind"
  QUEUE+=("$id")
done < <(jq -r '.jobs[] | [.id, .host, .dir, .kind] | @tsv' "$OUT/manifest.json")

# Edits QUEUE in this shell. A command substitution would discard that edit
# and the same job would be started again on the next pass.
next_id=""
take_next() {
  local i id host
  next_id=""
  for i in "${!QUEUE[@]}"; do
    id="${QUEUE[$i]}"
    [[ -n "$id" ]] || continue
    host="${JOB_HOST[$id]}"
    if [[ -n "${BUSY_HOST[$host]:-}" ]]; then
      continue
    fi
    QUEUE[$i]=""
    next_id="$id"
    return 0
  done
  return 1
}

queue_remaining() {
  local id
  for id in "${QUEUE[@]}"; do
    if [[ -n "$id" ]]; then
      return 0
    fi
  done
  return 1
}

pane_still_running() {
  local info names
  info="$(herdr pane process-info --pane "$1" 2>/dev/null || true)"
  names="$(printf '%s' "$info" | jq -r '
    .result.process_info.foreground_processes[]?
    | .name, .cmdline, ((.argv // []) | join(" "))
  ' 2>/dev/null || true)"
  # The sentinel is printed after Pi exits. This only waits until the
  # foreground is the pane shell again. An idle bash pane does not match.
  printf '%s\n' "$names" | grep -Eq '(^|/)(pi|bwrap|timeout)([[:space:]]|$)'
}

launch_job() {
  local pane="$1" id="$2" script
  script="$OUT/${JOB_DIR[$id]}/run.sh"
  if herdr pane run "$pane" bash "$script" >/dev/null; then
    PANE_JOB["$pane"]="$id"
    BUSY_HOST["${JOB_HOST[$id]}"]=1
    PANE_START["$pane"]="$(date +%s)"
    log "started $id on $pane"
    return 0
  fi
  log "pane $pane was not ready for $id; it stays queued"
  return 1
}

finish_job() {
  local pane="$1" id="$2" host meta code
  host="${JOB_HOST[$id]}"
  meta="$OUT/${JOB_DIR[$id]}/meta.txt"
  code="$(sed -n 's/^exit_code=//p' "$meta" 2>/dev/null | head -n 1)"
  unset "BUSY_HOST[$host]"
  unset "PANE_JOB[$pane]"
  unset "PANE_START[$pane]"
  log "finished $id on $pane (exit ${code:-unknown})"
}

any_busy() {
  local pane
  for pane in "${PANES[@]}"; do
    if [[ -n "${PANE_JOB[$pane]:-}" ]]; then
      return 0
    fi
  done
  return 1
}

free_pane() {
  local pane
  for pane in "${PANES[@]}"; do
    if [[ -z "${PANE_JOB[$pane]:-}" && -z "${PANE_STUCK[$pane]:-}" ]]; then
      return 0
    fi
  done
  return 1
}

while queue_remaining || any_busy; do
  for pane in "${PANES[@]}"; do
    if [[ -n "${PANE_STUCK[$pane]:-}" ]]; then
      continue
    fi
    id="${PANE_JOB[$pane]:-}"
    [[ -n "$id" ]] || continue
    # meta.txt is removed at launch and written again only after Pi exits.
    # The pane keeps old sentinel lines, so scrollback is not a completion signal.
    if [[ -f "$OUT/${JOB_DIR[$id]}/meta.txt" ]]; then
      if pane_still_running "$pane"; then
        continue
      fi
      sleep 2
      if pane_still_running "$pane"; then
        continue
      fi
      finish_job "$pane" "$id"
      continue
    fi
    if [[ "${JOB_KIND[$id]}" == "facet" ]]; then
      limit="$FACET_TIMEOUT"
    else
      limit="$ANSWER_TIMEOUT"
    fi
    now="$(date +%s)"
    start="${PANE_START[$pane]}"
    if (( now > start + limit + 90 )); then
      meta="$OUT/${JOB_DIR[$id]}/meta.txt"
      if [[ ! -f "$meta" ]]; then
        {
          echo "exit_code=124"
          echo "seconds=$((now - start))"
          echo "timeout=$limit"
          echo "kind=${JOB_KIND[$id]}"
          echo "dispatcher=timeout"
        } >"$meta"
      fi
      log "gave up waiting for $id on $pane; that pane will not be reused"
      finish_job "$pane" "$id"
      PANE_STUCK["$pane"]=1
    fi
  done

  if queue_remaining && ! any_busy && ! free_pane; then
    log "Jobs remain and every pane is stuck. Stopping the dispatcher."
    break
  fi

  for pane in "${PANES[@]}"; do
    if [[ -n "${PANE_JOB[$pane]:-}" || -n "${PANE_STUCK[$pane]:-}" ]]; then
      continue
    fi
    if ! queue_remaining; then
      break
    fi
    if ! take_next; then
      break
    fi
    id="$next_id"
    rm -f "$OUT/${JOB_DIR[$id]}/meta.txt"
    if ! launch_job "$pane" "$id"; then
      LAUNCH_FAILS["$id"]=$(( ${LAUNCH_FAILS[$id]:-0} + 1 ))
      if (( LAUNCH_FAILS["$id"] >= 10 )); then
        meta="$OUT/${JOB_DIR[$id]}/meta.txt"
        {
          echo "exit_code=1"
          echo "seconds=0"
          echo "timeout=0"
          echo "kind=${JOB_KIND[$id]}"
          echo "dispatcher=pane-not-ready"
        } >"$meta"
        log "could not start $id after 10 tries"
      else
        QUEUE+=("$id")
      fi
    fi
  done

  if any_busy || queue_remaining; then
    sleep 5
  fi
done

uv run python "$JOBS" finish --out "$OUT"
log "Summary: $OUT/summary.md"
if [[ "$CLEANUP" -eq 0 ]]; then
  log "Workspace $WS_ID is still open. Close it with: herdr workspace close $WS_ID"
fi

fail=0
expected="$(jq '.jobs | length' "$OUT/manifest.json")"
found="$(find "$OUT" -name meta.txt | wc -l)"
if [[ "$found" -lt "$expected" ]]; then
  log "Expected $expected meta.txt files and found $found"
  fail=1
fi
while IFS= read -r meta; do
  code="$(sed -n 's/^exit_code=//p' "$meta" | head -n 1)"
  if [[ "$code" != "0" ]]; then
    log "non-zero exit in $meta ($code)"
    fail=1
  fi
done < <(find "$OUT" -name meta.txt | sort)
exit "$fail"
