#!/data/data/com.termux/files/usr/bin/bash
# patterns.sh — Pattern Detection v0.5
# Читает cache.jsonl. Считает. Показывает.
# НЕ создаёт правил. Только наблюдает.

CACHE="$HOME/rumix/loop/cache.jsonl"

if [ ! -f "$CACHE" ]; then
    echo "Нет $CACHE"
    exit 1
fi

TOTAL=$(wc -l < "$CACHE")

echo "Pattern Detection — v0.5"
echo "Источник: cache.jsonl"
echo "Записей: $TOTAL"
echo ""

echo "--- A. MATCH ---"
Y=$(grep -c '"match":"yes"' "$CACHE" 2>/dev/null)
N=$(grep -c '"match":"no"' "$CACHE" 2>/dev/null)
NO_MATCH=$((TOTAL - Y - N))
[ "$TOTAL" -gt 0 ] && PY=$((Y * 100 / TOTAL)) || PY=0
[ "$TOTAL" -gt 0 ] && PN=$((N * 100 / TOTAL)) || PN=0
[ "$TOTAL" -gt 0 ] && PNO=$((NO_MATCH * 100 / TOTAL)) || PNO=0

echo "yes:  $Y ($PY%)"
echo "no:   $N ($PN%)"
echo "none: $NO_MATCH ($PNO%)"
echo ""

echo "--- B. EXIT ---"
E0=$(grep -c '"exit":0' "$CACHE" 2>/dev/null || echo 0)
ENZ=$((TOTAL - E0))
[ "$TOTAL" -gt 0 ] && PE0=$((E0 * 100 / TOTAL)) || PE0=0
[ "$TOTAL" -gt 0 ] && PENZ=$((ENZ * 100 / TOTAL)) || PENZ=0

echo "exit=0:   $E0 ($PE0%)"
echo "exit!=0:  $ENZ ($PENZ%)"
echo ""

echo "--- C. EXPECTED ---"
EX0=$(grep -c '"expected":"exit=0"' "$CACHE" 2>/dev/null || echo 0)
EXNONE=$((TOTAL - EX0))
[ "$TOTAL" -gt 0 ] && PEX0=$((EX0 * 100 / TOTAL)) || PEX0=0
[ "$TOTAL" -gt 0 ] && PEXNONE=$((EXNONE * 100 / TOTAL)) || PEXNONE=0

echo "exit=0:      $EX0 ($PEX0%)"
echo "отсутствует: $EXNONE ($PEXNONE%)"
echo ""

echo "--- D. PATTERNS ---"

P1_MATCH=$(grep '"expected":"exit=0"' "$CACHE" | grep '"exit":0' | grep -c '"match":"yes"' || echo 0)

if [ "$P1_MATCH" -ge 3 ]; then
    echo "[OBSERVED] expected=exit=0 + exit=0 + match=yes"
    echo "           Наблюдений: $P1_MATCH"
    echo "           Confidence: observed (>= 3)"
elif [ "$P1_MATCH" -ge 1 ]; then
    echo "[TENTATIVE] expected=exit=0 + exit=0 + match=yes"
    echo "            Наблюдений: $P1_MATCH"
    echo "            Confidence: tentative (< 3)"
else
    echo "[—] expected=exit=0 + exit=0 + match=yes — нет наблюдений"
fi
echo ""

P2=$((TOTAL - EX0))

if [ "$P2" -ge 3 ]; then
    echo "[OBSERVED] без expected + match=none"
    echo "           Наблюдений: $P2"
    echo "           Confidence: observed (>= 3)"
elif [ "$P2" -ge 1 ]; then
    echo "[TENTATIVE] без expected + match=none"
    echo "            Наблюдений: $P2"
    echo "            Confidence: tentative (< 3)"
else
    echo "[—] без expected + match=none — нет наблюдений"
fi
echo ""

echo "--- ПРИМЕЧАНИЕ ---"
echo "Pattern Detection не создаёт правил."
echo "Только наблюдает. Решение — за человеком."
