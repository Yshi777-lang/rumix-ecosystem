#!/data/data/com.termux/files/usr/bin/bash
# run.sh — Regression Runner v0.1
# Запускает все test_*.sh. Собирает PASS/FAIL.

TESTS_DIR="$HOME/rumix/agents/tests"
RESULTS_DIR="$TESTS_DIR/results"
TIMESTAMP=$(date '+%Y-%m-%d-%H%M')
RESULT_FILE="$RESULTS_DIR/run-$TIMESTAMP.log"

PASS=0
FAIL=0
TOTAL=0

echo "🌊 Regression Runner v0.1"
echo "Результат: $RESULT_FILE"
echo ""

for test_file in "$TESTS_DIR"/test_*.sh; do
    [ -e "$test_file" ] || continue
    name=$(basename "$test_file" .sh)
    TOTAL=$((TOTAL + 1))

    output=$(bash "$test_file" 2>&1)
    rc=$?

    if [ "$rc" -eq 0 ]; then
        echo "✅ $name"
        PASS=$((PASS + 1))
        echo "PASS: $name" >> "$RESULT_FILE"
    else
        echo "❌ $name"
        echo "$output" | sed 's/^/   /'
        FAIL=$((FAIL + 1))
        echo "FAIL: $name" >> "$RESULT_FILE"
        echo "$output" >> "$RESULT_FILE"
    fi
    echo "$output" >> "$RESULT_FILE"
    echo "---" >> "$RESULT_FILE"
done

echo ""
echo "─── ИТОГ ───"
echo "Всего:  $TOTAL"
echo "PASS:   $PASS"
echo "FAIL:   $FAIL"

echo "" >> "$RESULT_FILE"
echo "TOTAL: $TOTAL, PASS: $PASS, FAIL: $FAIL" >> "$RESULT_FILE"

[ "$FAIL" -eq 0 ] && exit 0 || exit 1
