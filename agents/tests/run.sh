#!/usr/bin/env bash
set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUMIX_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
TESTS_DIR="$RUMIX_ROOT/agents/tests"
RESULTS_DIR="$TESTS_DIR/results"
mkdir -p "$RESULTS_DIR"
export RUMIX_ROOT
TIMESTAMP="$(date '+%Y-%m-%d-%H%M%S')"
RESULT_FILE="$RESULTS_DIR/run-$TIMESTAMP.log"
PASS=0; FAIL=0; TOTAL=0
echo "🌊 Rumix Regression Runner"
echo "Root: $RUMIX_ROOT"
echo "Results: $RESULT_FILE"
echo
shopt -s nullglob
TEST_FILES=("$TESTS_DIR"/test_*.sh)
for test_file in "${TEST_FILES[@]}"; do
    name="$(basename "$test_file" .sh)"
    TOTAL=$((TOTAL + 1))
    echo "▶ $name"
    if output="$(bash "$test_file" 2>&1)"; then
        echo "✅ $name"; PASS=$((PASS + 1)); STATUS="PASS"
    else
        rc=$?; echo "❌ $name (exit $rc)"; echo "$output"; FAIL=$((FAIL + 1)); STATUS="FAIL"
    fi
    { echo "$STATUS: $name"; echo "$output"; echo "---"; } >> "$RESULT_FILE"
done
echo; echo "──── SUMMARY ────"
echo "TOTAL: $TOTAL"; echo "PASS: $PASS"; echo "FAIL: $FAIL"
{ echo; echo "TOTAL: $TOTAL, PASS: $PASS, FAIL: $FAIL"; } >> "$RESULT_FILE"
if [ "$TOTAL" -eq 0 ]; then echo "ERROR: No tests found"; exit 2; fi
[ "$FAIL" -eq 0 ]
