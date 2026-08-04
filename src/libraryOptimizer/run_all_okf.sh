#!/usr/bin/env bash
# Run libraryOptimizer over every OKF prompt example (sequential).
#
# Defaults match config/default.yaml:
#   task backend = NRP (model glm-5)
#   reflection / judge backend = NRP (model gpt-oss)
#
# Usage (from anywhere):
#   export NRP_API_KEY=…
#   ./src/libraryOptimizer/run_all_okf.sh
#
# Common overrides:
#   GEPA_BUDGET=20 N_SCENARIOS=8 ./src/libraryOptimizer/run_all_okf.sh
#   DRY_RUN=1 ./src/libraryOptimizer/run_all_okf.sh          # print only
#   BASELINE=0 ./src/libraryOptimizer/run_all_okf.sh         # skip baseline
#   GEN_SCENARIOS=1 ./src/libraryOptimizer/run_all_okf.sh    # gen-scenarios first
#   BACKEND=openrouter REFLECTION_BACKEND=openrouter ./src/libraryOptimizer/run_all_okf.sh
#   ONLY=name-description ./src/libraryOptimizer/run_all_okf.sh   # path substring filter
#   CONTINUE_ON_ERROR=0 ./src/libraryOptimizer/run_all_okf.sh     # abort on first failure
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# src/libraryOptimizer → repo root (parent of src/)
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "${REPO_ROOT}"

EXAMPLES_ROOT="${EXAMPLES_ROOT:-okf/prompt_examples}"
RUNS_ROOT="${RUNS_ROOT:-src/libraryOptimizer/runs/okf-batch}"
MAIN=(uv run python src/libraryOptimizer/main.py)

BACKEND="${BACKEND:-nrp}"
REFLECTION_BACKEND="${REFLECTION_BACKEND:-nrp}"
JUDGE="${JUDGE:-reflection}"
GEPA_BUDGET="${GEPA_BUDGET:-40}"
N_SCENARIOS="${N_SCENARIOS:-12}"
NUM_THREADS="${NUM_THREADS:-4}"
SEED="${SEED:-0}"
AUTO="${AUTO:-light}"

# 1 = run baseline before optimize; 0 = skip
BASELINE="${BASELINE:-1}"
# 1 = gen-scenarios explicitly before optimize; 0 = let optimize auto-gen if missing
GEN_SCENARIOS="${GEN_SCENARIOS:-0}"
# 1 = print commands only
DRY_RUN="${DRY_RUN:-0}"
# 1 = keep going after a failed prompt; 0 = exit on first failure
CONTINUE_ON_ERROR="${CONTINUE_ON_ERROR:-1}"
# Optional path substring filter (e.g. ONLY=citation or ONLY=name-description)
ONLY="${ONLY:-}"

COMMON=(
  --backend "${BACKEND}"
  --reflection-backend "${REFLECTION_BACKEND}"
  --judge "${JUDGE}"
  --auto "${AUTO}"
  --num-threads "${NUM_THREADS}"
  --seed "${SEED}"
  --n "${N_SCENARIOS}"
  --gepa-budget "${GEPA_BUDGET}"
)

if [[ ! -d "${EXAMPLES_ROOT}" ]]; then
  echo "error: examples root not found: ${EXAMPLES_ROOT}" >&2
  echo "  (cwd=${REPO_ROOT})" >&2
  exit 1
fi

mapfile -t PROMPTS < <(
  find "${EXAMPLES_ROOT}" -type f -name '*.md' ! -name 'README.md' | sort
)

if [[ ${#PROMPTS[@]} -eq 0 ]]; then
  echo "error: no prompt examples under ${EXAMPLES_ROOT}" >&2
  exit 1
fi

if [[ -n "${ONLY}" ]]; then
  filtered=()
  for p in "${PROMPTS[@]}"; do
    if [[ "${p}" == *"${ONLY}"* ]]; then
      filtered+=("${p}")
    fi
  done
  PROMPTS=("${filtered[@]}")
  if [[ ${#PROMPTS[@]} -eq 0 ]]; then
    echo "error: ONLY=${ONLY@Q} matched no prompts under ${EXAMPLES_ROOT}" >&2
    exit 1
  fi
fi

slug_for() {
  # okf/prompt_examples/metadata-schema/core-elements/name-description.md
  # → metadata-schema-core-elements-name-description
  local rel="$1"
  rel="${rel#${EXAMPLES_ROOT}/}"
  rel="${rel#./}"
  rel="${rel%.md}"
  echo "${rel//\//-}"
}

run_cmd() {
  if [[ "${DRY_RUN}" == "1" ]]; then
    printf '[dry-run]'
    printf ' %q' "$@"
    printf '\n'
    return 0
  fi
  "$@"
}

# Run a libraryOptimizer subcommand; tee real runs into the batch log.
invoke() {
  if [[ "${DRY_RUN}" == "1" ]]; then
    run_cmd "$@"
    return 0
  fi
  # shellcheck disable=SC2068
  "$@" 2>&1 | tee -a "${LOG}"
  return "${PIPESTATUS[0]}"
}

mkdir -p "${RUNS_ROOT}"
LOG="${RUNS_ROOT}/batch.log"
SUMMARY="${RUNS_ROOT}/batch-summary.txt"
: >"${LOG}"
: >"${SUMMARY}"

echo "libraryOptimizer OKF batch" | tee -a "${LOG}"
echo "  repo=${REPO_ROOT}" | tee -a "${LOG}"
echo "  examples=${EXAMPLES_ROOT} (${#PROMPTS[@]} prompt(s))" | tee -a "${LOG}"
echo "  runs=${RUNS_ROOT}" | tee -a "${LOG}"
echo "  backend=${BACKEND} reflection=${REFLECTION_BACKEND} judge=${JUDGE}" | tee -a "${LOG}"
echo "  gepa_budget=${GEPA_BUDGET} n_scenarios=${N_SCENARIOS} baseline=${BASELINE} gen_scenarios=${GEN_SCENARIOS}" | tee -a "${LOG}"
echo "  dry_run=${DRY_RUN} continue_on_error=${CONTINUE_ON_ERROR}" | tee -a "${LOG}"
echo | tee -a "${LOG}"

ok=0
fail=0
failed_list=()

for prompt in "${PROMPTS[@]}"; do
  slug="$(slug_for "${prompt}")"
  workdir="${RUNS_ROOT}/${slug}"
  mkdir -p "${workdir}"

  echo "======== ${prompt} → ${workdir} ========" | tee -a "${LOG}"
  status=0

  if [[ "${GEN_SCENARIOS}" == "1" ]]; then
    invoke "${MAIN[@]}" gen-scenarios \
      --prompt "${prompt}" \
      --workdir "${workdir}" \
      --backend "${BACKEND}" \
      --num-threads "${NUM_THREADS}" \
      --seed "${SEED}" \
      --n "${N_SCENARIOS}" \
      || status=$?
  fi

  if [[ "${status}" -eq 0 && "${BASELINE}" == "1" ]]; then
    invoke "${MAIN[@]}" baseline \
      --prompt "${prompt}" \
      --workdir "${workdir}" \
      "${COMMON[@]}" \
      || status=$?
  fi

  if [[ "${status}" -eq 0 ]]; then
    invoke "${MAIN[@]}" optimize \
      --prompt "${prompt}" \
      --workdir "${workdir}" \
      "${COMMON[@]}" \
      || status=$?
  fi

  if [[ "${status}" -eq 0 ]]; then
    echo "OK  ${slug}" | tee -a "${SUMMARY}"
    ok=$((ok + 1))
  else
    echo "FAIL ${slug} (exit ${status})" | tee -a "${SUMMARY}"
    fail=$((fail + 1))
    failed_list+=("${prompt}")
    if [[ "${CONTINUE_ON_ERROR}" != "1" ]]; then
      echo "aborting (CONTINUE_ON_ERROR=0)" | tee -a "${LOG}"
      break
    fi
  fi
  echo | tee -a "${LOG}"
done

echo "======== summary ========" | tee -a "${LOG}"
echo "ok=${ok} fail=${fail} total=$((ok + fail))" | tee -a "${LOG}" | tee -a "${SUMMARY}"
if [[ ${#failed_list[@]} -gt 0 ]]; then
  echo "failed prompts:" | tee -a "${LOG}" | tee -a "${SUMMARY}"
  for p in "${failed_list[@]}"; do
    echo "  - ${p}" | tee -a "${LOG}" | tee -a "${SUMMARY}"
  done
fi
echo "log:     ${LOG}"
echo "summary: ${SUMMARY}"
echo "runs:    ${RUNS_ROOT}/<slug>/"

if [[ "${fail}" -gt 0 ]]; then
  exit 1
fi
