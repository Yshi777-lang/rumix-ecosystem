#!/data/data/com.termux/files/usr/bin/bash
# loop-log.sh — читалка cache.jsonl
# Использование: bash loop-log.sh [N]
# N — сколько последних записей (по умолчанию 10)

CACHE="$HOME/rumix/loop/cache.jsonl"
N="${1:-10}"

if [ ! -f "$CACHE" ]; then
    echo "❌ Нет $CACHE"
    exit 1
fi

echo "🌊 Loop Experience Log — последние $N"
echo ""

tail -n "$N" "$CACHE" | while IFS= read -r line; do
    # Парсим поля через grep/sed — без jq
    name=$(echo "$line" | sed -n 's/.*"name":"\([^"]*\)".*/\1/p')
    ts=$(echo "$line" | sed -n 's/.*"ts":"\([^"]*\)".*/\1/p')
    exit_code=$(echo "$line" | sed -n 's/.*"exit":\([0-9]*\).*/\1/p')
    expected=$(echo "$line" | sed -n 's/.*"expected":"\([^"]*\)".*/\1/p')
    match=$(echo "$line" | sed -n 's/.*"match":"\([^"]*\)".*/\1/p')

    [ -z "$match" ] && match="none"
    [ -z "$expected" ] && expected="none"

    if [ "$match" = "yes" ]; then
        icon="✅"
    elif [ "$match" = "no" ]; then
        icon="❌"
    else
        icon="➖"
    fi

    echo "$icon  $ts  $name  exit=$exit_code  expected=$expected  match=$match"
done

echo ""
TOTAL=$(wc -l < "$CACHE")
echo "Всего записей: $TOTAL"
