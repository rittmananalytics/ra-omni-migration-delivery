#!/usr/bin/env bash
# Headless driver for turns 1-5 of docs/looker-to-omni-migration-test-script.md.
# Run from the repo root:
#   bash harness/run_test.sh        # full run from turn 1
#   bash harness/run_test.sh 3      # resume from turn 3 (continues the conversation)
# Streams every tool call and response live via harness/format_stream.py.
# Cutover (turn 6) is deliberately NOT here: it is a human ruling, given in an
# interactive session after reviewing the equivalency report.
set -euo pipefail
LOG=harness_run.log
START_AT="${1:-1}"

if [ "$START_AT" = "1" ] && grep -q '<MODEL_ID>' harness/turns/turn1.txt; then
  echo "Fill <MODEL_ID> in harness/turns/turn1.txt first (see Part A step 5.4)." >&2
  exit 1
fi

send() {  # send <turn-number> <continue-flag> — streams live, fills last_turn.txt
  local n="$1" cflag="$2"
  echo "=== $(date -u +%FT%TZ) turn: harness/turns/turn${n}.txt ===" | tee -a "$LOG"
  # shellcheck disable=SC2086
  claude -p $cflag --output-format stream-json --verbose --permission-mode acceptEdits \
    "$(cat "harness/turns/turn${n}.txt")" | python3 harness/format_stream.py | tee -a "$LOG"
}

gate() {  # gate <turn-number> <expect-regex>
  if ! grep -qiE "$2" last_turn.txt; then
    echo "GATE NOT REACHED after turn $1 (expected /$2/). Stopping for a human: open 'claude -c' to see what it needs." | tee -a "$LOG"
    exit 1
  fi
}

declare -A EXPECT=(
  [1]="parked|migration plan"
  [2]="target setup|model batch|branch"
  [3]="needs_human|batch .* (ready|complete|validated)"
  [4]="equivalency|parity"
  [5]="PASS|ACCEPTED|not PASS"
)

for n in 1 2 3 4 5; do
  [ "$n" -lt "$START_AT" ] && continue
  if [ "$n" = "1" ]; then send 1 ""; else send "$n" "-c"; fi
  gate "$n" "${EXPECT[$n]}"
done

echo "Turns ${START_AT}-5 complete. CUTOVER IS MANUAL: review the equivalency report, then give the turn 6 ruling yourself in an interactive session (claude -c)." | tee -a "$LOG"
