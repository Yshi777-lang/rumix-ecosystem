#!/data/data/com.termux/files/usr/bin/bash
# loop-v0.3.sh — Rumix Loop v0.3
# Clipboard + File Queue + Expected.
#
# Формат <RUMIX>:
#   <RUMIX>
#   # expected: exit=0
#   echo "hello"
#   </RUMIX>
#
# Проверки: exit=0 | exit!=0 | contains: <text> | match: <regex>

LOOP_DIR="$HOME/rumix/loop"
OUT_DIR="$LOOP_DIR/out"
IN_DIR="$LOOP_DIR/in"
DONE_DIR="$LOOP_DIR/done"
CACHE="$LOOP_DIR/cache.jsonl"
QUEUE="$LOOP_DIR/queue.txt"
CACHE_ARCHIVE="$LOOP_DIR/archive"
CACHE_MAX_LINES="${CACHE_MAX_LINES:-10000}"
STATE_FILE="$LOOP_DIR/state.json"
IDLE_TIMEOUT_SEC="${IDLE_TIMEOUT_SEC:-600}"
LAST_ACTIVITY="$(date +%s)"

# Записать состояние в state.json
write_state() {
    local state="$1"
    local enabled="${2:-true}"
    python3 -c "
import json, os
from datetime import datetime
state = {
    'schema_version': 1,
    'enabled': $([ \"$enabled\" = 'true' ] && echo True || echo False),
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

echo "🌊 Rumix Loop v0.3"
echo "   OUT:  $OUT_DIR"
echo "   IN:   $IN_DIR"
echo "   DONE: $DONE_DIR"
echo "   Триггер буфера: <RUMIX>..."
echo "   Expected: # expected: exit=0"
echo ""
write_state "idle" "true"
echo "Жду... (Ctrl+C — остановка)"
echo ""

# Проверка expected
check_expected() {
    local expected="$1"
    local output="$2"
    local exit_code="$3"

    [ -z "$expected" ] && { echo "none"; return; }

    if [ "$expected" = "exit=0" ]; then
        [ "$exit_code" = "0" ] && echo "yes" || echo "no"
    elif [ "$expected" = "exit!=0" ]; then
        [ "$exit_code" != "0" ] && echo "yes" || echo "no"
    elif [[ "$expected" == contains:* ]]; then
        local text="${expected#contains: }"
        echo "$output" | grep -qF "$text" && echo "yes" || echo "no"
    elif [[ "$expected" == match:* ]]; then
        local regex="${expected#match: }"
        echo "$output" | grep -qE "$regex" && echo "yes" || echo "no"
    else
        echo "unknown"
    fi
}

# Выполнить содержимое
run_content() {
    local name="$1"
    local content="$2"

    # Извлекаем expected — ищем в первых 3 строках, пропуская пустые
    local expected=""
    local head3=$(echo "$content" | head -3)
    local exp_line=$(echo "$head3" | grep -m1 '^# expected:')
    if [ -n "$exp_line" ]; then
        expected=$(echo "$exp_line" | sed 's/^# expected:[[:space:]]*//')
        # Удаляем строку с expected из content
        content=$(echo "$content" | grep -v '^# expected:' | sed '/./,$!d')
    fi
    # Убираем пустые строки в начале content
    content=$(echo "$content" | sed '/./,$!d')

    local ts=$(date '+%Y-%m-%d %H:%M:%S')
    local result_file="$IN_DIR/${name}.result"

    echo "▶ $name — выполняется..."

    local output=$(echo "$content" | bash 2>&1)
    local exit_code=$?
    local match=$(check_expected "$expected" "$output" "$exit_code")

    {
        echo "=== RUMIX_RESULT ==="
        echo "name: $name"
        echo "timestamp: $ts"
        echo "expected: ${expected:-none}"
        echo "match: $match"
        echo "--- stdout ---"
        echo "$output"
        echo "--- end ---"
        echo "exit_code: $exit_code"
        echo "=== END ==="
    } > "$result_file"

    echo "✅ $name — exit=$exit_code, match=$match"

    # Логируем в cache
    echo "{\"schema_version\":1,\"name\":\"$name\",\"ts\":\"$ts\",\"exit\":$exit_code,\"expected\":\"$expected\",\"match\":\"$match\"}" >> "$CACHE"
}

# Ротация cache: если > CACHE_MAX_LINES, архивировать первое половину
rotate_cache() {
    if [ ! -f "$CACHE" ]; then
        return 0
    fi
    local lines
    lines=$(wc -l < "$CACHE" 2>/dev/null || echo 0)
    if [ "$lines" -le "$CACHE_MAX_LINES" ]; then
        return 0
    fi
    mkdir -p "$CACHE_ARCHIVE"
    local keep=$((CACHE_MAX_LINES / 2))
    local ts
    ts=$(date '+%Y-%m-%d-%H%M')
    local archive_file="$CACHE_ARCHIVE/cache-${ts}.jsonl"
    local tail_lines=$((lines - keep))

    # Первые tail_lines → в архив
    head -n "$tail_lines" "$CACHE" > "$archive_file"
    # Последние keep → обратно в cache
    tail -n "$keep" "$CACHE" > "$CACHE.tmp" && mv "$CACHE.tmp" "$CACHE"

    echo "🗄  Cache ротация: $tail_lines → $archive_file, оставлено $keep"
    gzip -f "$archive_file" 2>/dev/null || true
}

# Ротация cache перед началом работы
# Trap на выход
trap 'write_state "stopped" "false"; echo "💤 Loop остановлен."; exit 0' SIGINT SIGTERM

rotate_cache

counter=0

# Consent на ресурсы: проверить модель + сервис перед стартом
consent_check() {
    local issues=0
    local msg=""

    if [ ! -f "$HOME/models/qwen3-0.6b-q4.gguf" ]; then
        msg="${msg}\n   ❌ Модель не найдена: ~/models/qwen3-0.6b-q4.gguf"
        issues=$((issues+1))
    fi

    if ! curl -s --max-time 3 http://127.0.0.1:8080/v1/models 2>/dev/null | grep -q "qwen"; then
        msg="${msg}\n   ❌ llama-server не отвечает. Запусти: sv up neon"
        issues=$((issues+1))
    fi

    if [ "$issues" -gt 0 ]; then
        echo "⚠️  Loop: проблемы с ресурсами:"
        echo -e "$msg"
        echo ""
        if [ "${LOOP_NONINTERACTIVE:-0}" = "1" ]; then answer="y"; echo "y (non-interactive)"; else read -r -p "Продолжить? (y/n): " answer; fi
        [ "$answer" != "y" ] && exit 1
    fi
}

consent_check

while true; do
    # Проверка таймаута бездействия
    NOW="$(date +%s)"
    IDLE="$((NOW - LAST_ACTIVITY))"
    if [ "$IDLE" -ge "$IDLE_TIMEOUT_SEC" ]; then
        write_state "stopped" "false"
        echo "💤 Loop остановлен по таймауту бездействия (${IDLE_TIMEOUT_SEC}s)."
        exit 0
    fi

    # === 1. Файлы из очереди (FIFO) ===
    if [ -f "$QUEUE" ] && [ -s "$QUEUE" ]; then
        name=$(head -1 "$QUEUE")
        if [ -n "$name" ] && [ -f "$OUT_DIR/${name}.sh" ]; then
            content=$(cat "$OUT_DIR/${name}.sh")
            run_content "$name" "$content"
            mv "$OUT_DIR/${name}.sh" "$DONE_DIR/${name}.sh"
            tail -n +2 "$QUEUE" > "$QUEUE.tmp" && mv "$QUEUE.tmp" "$QUEUE"
            LAST_ACTIVITY="$(date +%s)"
        else
            echo "⚠️  Задача '$name' в очереди, но файла нет"
            tail -n +2 "$QUEUE" > "$QUEUE.tmp" && mv "$QUEUE.tmp" "$QUEUE"
        fi
    else
        # Fallback: если queue.txt пуст — берём из out/ как раньше
        for file in "$OUT_DIR"/*.sh; do
            [ -e "$file" ] || continue
            name=$(basename "$file" .sh)
            content=$(cat "$file")
            run_content "$name" "$content"
            mv "$file" "$DONE_DIR/${name}.sh"
            LAST_ACTIVITY="$(date +%s)"
            break
        done
    fi

    # === 2. Буфер ===
    clipboard=$(timeout 3 termux-clipboard-get 2>/dev/null || true)
    if echo "$clipboard" | head -1 | grep -q '^<RUMIX>'; then
        counter=$((counter + 1))
        name=$(printf "clip-%03d" "$counter")
        content=$(echo "$clipboard" | sed '1s/^<RUMIX>//; $s/<\/RUMIX>$//')
        echo " " | termux-clipboard-set
        sleep 2
        run_content "$name" "$content"
        sleep 2
        cat "$IN_DIR/${name}.result" | termux-clipboard-set
        sleep 1
        echo "   → результат → буфер"
    fi

    sleep 2
done
