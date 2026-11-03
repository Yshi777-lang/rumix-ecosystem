#!/data/data/com.termux/files/usr/bin/bash
# loop.sh — Rumix Loop v0.1
# File Queue. Watcher. Executor. Result Writer.
#
# Как работает:
#   1. Смотрит на ~/rumix/loop/out/
#   2. Каждый файл *.sh — выполняет
#   3. Пишет результат в ~/rumix/loop/in/<name>.result
#   4. Переносит выполненный в ~/rumix/loop/done/
#   5. Ждёт следующий
#
# Запуск: bash ~/rumix/loop/loop.sh

LOOP_DIR="$HOME/rumix/loop"
OUT_DIR="$LOOP_DIR/out"
IN_DIR="$LOOP_DIR/in"
DONE_DIR="$LOOP_DIR/done"
STATE_FILE="$LOOP_DIR/state.json"
IDLE_TIMEOUT_SEC="${IDLE_TIMEOUT_SEC:-600}"   # 10 минут по умолчанию
LAST_ACTIVITY="$(date +%s)"

# Записать состояние в state.json
write_state() {
    local state="$1"
    local enabled="${2:-true}"
    python3 -c "
import json, os, sys
from datetime import datetime
state = {
    'schema_version': 1,
    'enabled': $([ "$enabled" = 'true' ] && echo True || echo False),
    'state': '$state',
    'pid': os.getpid(),
    'started_at': os.environ.get('LOOP_STARTED_AT', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
    'last_activity': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'idle_timeout_sec': int(os.environ.get('IDLE_TIMEOUT_SEC', '600')),
}
with open('$STATE_FILE', 'w') as f:
    json.dump(state, f, ensure_ascii=False, indent=2)
"
}

export LOOP_STARTED_AT="$(date '+%Y-%m-%d %H:%M:%S')"

echo "🌊 Rumix Loop v0.1"
echo "   OUT:  $OUT_DIR"
echo "   IN:   $IN_DIR"
echo "   DONE: $DONE_DIR"
echo ""
write_state "idle" "true"
echo "Жду файлы в out/ (Ctrl+C — остановка)..."
echo ""

# При выходе — записать остановку
trap 'write_state "stopped" "false"; echo "💤 Loop остановлен."; exit 0' SIGINT SIGTERM

while true; do
    # Проверка таймаута бездействия
    NOW="$(date +%s)"
    IDLE="$((NOW - LAST_ACTIVITY))"
    if [ "$IDLE" -ge "$IDLE_TIMEOUT_SEC" ]; then
        write_state "stopped" "false"
        echo "💤 Loop остановлен по таймауту бездействия (${IDLE_TIMEOUT_SEC}s)."
        exit 0
    fi
    # Ищем *.sh в out/
    for file in "$OUT_DIR"/*.sh; do
        # Если файл не существует (нет совпадений) — пропускаем
        [ -e "$file" ] || continue

        name=$(basename "$file" .sh)
        ts=$(date '+%Y-%m-%d %H:%M:%S')

        write_state "working" "true"
    echo "▶ $name — выполняется..."

        # Выполняем и пишем результат
        result_file="$IN_DIR/${name}.result"
        {
            echo "=== RUMIX_RESULT ==="
            echo "name: $name"
            echo "timestamp: $ts"
            echo "--- stdout ---"

            # Выполняем как bash-скрипт, ловим всё
            # ПРОВЕРКА ЧЕРЕЗ LOOP GATE
            if ! bash ~/rumix/loop/loop-gate.sh "$file"; then
                echo "Loop Gate: выполнение отклонено."
                mv "$file" "$DONE_DIR/${name}.rejected"
                continue
            fi
            output=$(bash "$file" 2>&1)
            exit_code=$?

            echo "$output"
            echo "--- end ---"
            echo "exit_code: $exit_code"
            echo "=== END ==="
        } > "$result_file"

        echo "✅ $name — exit=$exit_code, → in/${name}.result"

        # Переносим выполненный в done/
        mv "$file" "$DONE_DIR/${name}.sh"
        LAST_ACTIVITY="$(date +%s)"
        write_state "idle" "true"
    done

    sleep 2
done
