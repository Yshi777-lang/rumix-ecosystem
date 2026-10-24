#!/data/data/com.termux/files/usr/bin/bash
# Неон — управление локальным LLM
# Неоновый шёпот. 🤖

# Модель: из ~/.neon_model или по умолчанию
MODEL_FILE="$HOME/.neon_model"
DEFAULT_MODEL="$HOME/models/qwen3-0.6b-q4.gguf"
if [ -f "$MODEL_FILE" ]; then
    MODEL=$(cat "$MODEL_FILE")
else
    MODEL="$DEFAULT_MODEL"
fi
PORT=8080
LOG="$HOME/models/neon.log"

start() {
    if pgrep -f "llama-server" > /dev/null; then
        echo "✅ Неон уже запущен (PID: $(pgrep -f llama-server | head -1))"
        return
    fi
    echo "🚀 Запускаю гномика..."
    termux-wake-lock
    nohup llama-server -m "$MODEL" -c 8192 -t 8 -b 512 --chat-template-kwargs '{"enable_thinking": false}' --host 127.0.0.1 --port $PORT > "$LOG" 2>&1 &
    sleep 5
    if curl -s http://127.0.0.1:$PORT/v1/models > /dev/null 2>&1; then
        echo "✅ Неон жив (PID: $(pgrep -f llama-server | head -1))"
    else
        echo "⚠️  Неон не отвечает. Лог: $LOG"
    fi
}

stop() {
    if pgrep -f "llama-server" > /dev/null; then
        pkill -f "llama-server"
        termux-wake-unlock
        echo "🛑 Неон остановлен"
    else
        echo "⚠️  Неон не запущен"
    fi
}

status() {
    if pgrep -f "llama-server" > /dev/null; then
        echo "✅ Неон жив (PID: $(pgrep -f llama-server | head -1))"
        curl -s http://127.0.0.1:$PORT/v1/models | head -c 100
        echo ""
    else
        echo "⚠️  Неон не запущен"
    fi
}

check() {
    echo "=== Неон: проверка ==="
    OK=0
    FAIL=0
    if pgrep -f "llama-server" > /dev/null; then
        PID=$(pgrep -f "llama-server" | head -1)
        echo "✅ Процесс жив (PID: $PID)"
        OK=$((OK+1))
    else
        echo "❌ Процесс не найден"
        echo "   → Запусти: neon start"
        return
    fi
    if curl -s --max-time 3 http://127.0.0.1:$PORT/v1/models > /dev/null 2>&1; then
        echo "✅ Порт $PORT отвечает"
        OK=$((OK+1))
    else
        echo "⚠️  Порт не отвечает"
        FAIL=$((FAIL+1))
    fi
    if [ -f "$MODEL" ]; then
        SIZE=$(du -h "$MODEL" | cut -f1)
        echo "✅ Модель: $(basename $MODEL) ($SIZE)"
        OK=$((OK+1))
    else
        echo "❌ Модель не найдена"
        FAIL=$((FAIL+1))
    fi
    if command -v termux-wake-lock > /dev/null 2>&1; then
        echo "✅ Wakelock доступен"
        OK=$((OK+1))
    fi
    echo -n "⏱  Тест ответа... "
    T0=$(date +%s%N)
    RESP=$(curl -s --max-time 15 http://127.0.0.1:$PORT/v1/chat/completions \
        -H "Content-Type: application/json" \
        -d '{"model":"qwen","messages":[{"role":"user","content":"ok"}],"max_tokens":5}' 2>/dev/null)
    T1=$(date +%s%N)
    ELAPSED_MS=$(( (T1 - T0) / 1000000 ))
    if echo "$RESP" | grep -q "choices"; then
        echo "✅ ${ELAPSED_MS}ms"
        OK=$((OK+1))
    else
        echo "❌ нет ответа"
        FAIL=$((FAIL+1))
    fi
    echo ""
    if [ $FAIL -eq 0 ]; then
        echo "🌊 Всё готово. OK: $OK"
    else
        echo "⚠️  Проблемы. OK: $OK, FAIL: $FAIL"
    fi
}


model() {
    echo "=== Выбор модели Неона ==="
    echo ""
    MODELS=$(ls -1 "$HOME/models"/*.gguf 2>/dev/null)
    if [ -z "$MODELS" ]; then
        echo "❌ Нет моделей в ~/models/"
        return 1
    fi

    # Если передан аргумент — установить напрямую
    if [ -n "$2" ]; then
        FULL="$HOME/models/$2"
        if [ -f "$FULL" ]; then
            echo "$FULL" > "$HOME/.neon_model"
            echo "✅ Модель установлена: $2"
            echo "   Перезапусти: neon restart"
            return 0
        else
            echo "❌ Модель не найдена: $2"
            return 1
        fi
    fi

    # Иначе — показать список и выбрать
    echo "Доступные модели:"
    i=1
    for m in $MODELS; do
        SIZE=$(du -h "$m" | cut -f1)
        NAME=$(basename "$m")
        MARK=""
        [ "$m" = "$MODEL" ] && MARK=" ← текущая"
        echo "  $i) $NAME ($SIZE)$MARK"
        i=$((i+1))
    done
    echo ""
    echo -n "Выбери номер (или Enter для отмены): "
    read -r NUM
    [ -z "$NUM" ] && { echo "Отменено"; return 0; }
    SELECTED=$(echo "$MODELS" | sed -n "${NUM}p")
    if [ -n "$SELECTED" ]; then
        echo "$SELECTED" > "$HOME/.neon_model"
        echo "✅ Модель установлена: $(basename $SELECTED)"
        echo "   Перезапусти: neon restart"
    else
        echo "❌ Неверный номер"
    fi
}

restart() {
    stop
    sleep 2
    start
}

case "${1:-start}" in
    start) start ;;
    stop) stop ;;
    status) status ;;
    check) check ;;
    model) shift; model "$@" ;;
    restart) restart ;;
    *) echo "Usage: neon {start|stop|status|check|model|restart}" ;;
esac
