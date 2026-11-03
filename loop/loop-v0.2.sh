#!/data/data/com.termux/files/usr/bin/bash
# loop-v0.2.sh — Rumix Loop v0.2
# Clipboard + File Queue.
#
# Триггер: буфер содержит <RUMIX>...</RUMIX>
# Или: файл *.sh в out/
#
# Результат: пишется в in/<name>.result И в буфер с тегом <RUMIX_RESULT>

LOOP_DIR="$HOME/rumix/loop"
OUT_DIR="$LOOP_DIR/out"
IN_DIR="$LOOP_DIR/in"
DONE_DIR="$LOOP_DIR/done"
CACHE="$LOOP_DIR/cache.jsonl"

echo "🌊 Rumix Loop v0.2"
echo "   OUT:  $OUT_DIR"
echo "   IN:   $IN_DIR"
echo "   DONE: $DONE_DIR"
echo "   Триггер буфера: <RUMIX>...</RUMIX>"
echo ""
echo "Жду... (Ctrl+C — остановка)"
echo ""

# Функция: выполнить содержимое
run_content() {
    local name="$1"
    local content="$2"
    local ts=$(date '+%Y-%m-%d %H:%M:%S')
    local result_file="$IN_DIR/${name}.result"

    echo "▶ $name — выполняется..."

    {
        echo "=== RUMIX_RESULT ==="
        echo "name: $name"
        echo "timestamp: $ts"
        echo "--- stdout ---"
        output=$(echo "$content" | bash 2>&1)
        exit_code=$?
        echo "$output"
        echo "--- end ---"
        echo "exit_code: $exit_code"
        echo "=== END ==="
    } > "$result_file"

    echo "✅ $name — exit=$exit_code"

    echo "   → in/${name}.result"

    # Логируем в cache
    echo "{\"name\":\"$name\",\"ts\":\"$ts\",\"exit\":$exit_code}" >> "$CACHE"
}

# Счётчик для имён из буфера
counter=0

while true; do
    # === 1. Файлы в out/ ===
    for file in "$OUT_DIR"/*.sh; do
        [ -e "$file" ] || continue
        name=$(basename "$file" .sh)
        content=$(cat "$file")
        run_content "$name" "$content"
        mv "$file" "$DONE_DIR/${name}.sh"
    done

    # === 2. Буфер ===
    clipboard=$(termux-clipboard-get 2>/dev/null)
    if echo "$clipboard" | head -1 | grep -q '^<RUMIX>'; then
        counter=$((counter + 1))
        name=$(printf "clip-%03d" "$counter")
        # Убираем теги <RUMIX> и </RUMIX>
        content=$(echo "$clipboard" | sed '1s/^<RUMIX>//; $s/<\/RUMIX>$//')
        # 1. Очищаем буфер (чтобы не выполнять дважды)
        echo " " | termux-clipboard-set
        sleep 2
        # 2. Выполняем
        run_content "$name" "$content"
        # 3. Пишем результат в буфер
        sleep 2
        cat "$IN_DIR/${name}.result" | termux-clipboard-set
        sleep 1
        echo "   → результат → буфер"
    fi

    sleep 2
done
