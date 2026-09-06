#!/usr/bin/env bash
# Headless driver for turns 1-5 of docs/looker-to-omni-migration-test-script.md.
# Run from the repo root: bash harness/run_test.sh
# Cutover (turn 6) is deliberately NOT here: it is a human ruling, given in an
# interactive session after reviewing the equivalency report.
set -euo pipefail
LOG=harness_run.log
# QUIET=1 bash harness/run_test.sh prints only each turn's final response;
# the default (--verbose) streams tool calls and intermediate output so you
# can watch the orchestrator work.
FLAGS=(--permission-mode acceptEdits)
[ "${QUIET:-0}" = "1" ] || FLAGS+=(--verbose)

if grep -q '<MODEL_ID>' harness/turns/turn1.txt; then
  echo "Fill <MODEL_ID> in harness/turns/turn1.txt first (see Part A step 5.4)." >&2
  exit 1
fi

run_turn() {  # run_turn <file> <expect-regex>
  local file="$1" expect="$2"
  echo "=== $(date -u +%FT%TZ) turn: $file ===" | tee -a "$LOG"
  claude -p -c "${FLAGS[@]}" "$(cat "$file")" | tee -a "$LOG" > last_turn.txt
  if ! grep -qiE "$expect" last_turn.txt; then
    echo "GATE NOT REACHED after $file (expected /$expect/). Stopping for a human." | tee -a "$LOG"
    exit 1
  fi
}

# Turn 1 starts the conversation (no -c)
echo "=== $(date -u +%FT%TZ) turn: harness/turns/turn1.txt ===" | tee -a "$LOG"
claude -p "${FLAGS[@]}" "$(cat harness/turns/turn1.txt)" | tee -a "$LOG" > last_turn.txt
grep -qiE "parked|migration plan" last_turn.txt || { echo "Turn 1 did not reach the plan. Stopping." | tee -a "$LOG"; exit 1; }

run_turn harness/turns/turn2.txt "target setup|model batch|branch"
run_turn harness/turns/turn3.txt "needs_human|batch .* (ready|complete|validated)"
run_turn harness/turns/turn4.txt "equivalency|parity"
run_turn harness/turns/turn5.txt "PASS|ACCEPTED|not PASS"

echo "Turns 1-5 complete. CUTOVER IS MANUAL: review the equivalency report, then give the turn 6 ruling yourself in an interactive session." | tee -a "$LOG"
