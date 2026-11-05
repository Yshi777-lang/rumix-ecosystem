#!/data/data/com.termux/files/usr/bin/bash
# launch-all.sh — поднять дом: память → Неон → Shell → Сканер.
# Без pkill: всё через svc-manager (runit или PID-файлы).
# Без «голого» http://127.0.0.1:8001: открываем URL с токеном, иначе API ответит 401.

ECO_DIR="${RUMIX_ECO_DIR:-$HOME/rumix-ecosystem}"
RUMIX_DIR="${RUMIX_DATA_DIR:-$HOME/rumix}"
SVC="$ECO_DIR/scripts/svc-manager.sh"
SHELL_PORT=8001
NEON_PORT=8080
mkdir -p "$ECO_DIR/logs" "$RUMIX_DIR/logs"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"; }

free_mb() {
    free -m 2>/dev/null | awk '/Mem:/ {print ($7 != "" ? $7 : $4)}'
}

http_ok() { curl -s -o /dev/null -m 2 -w '%{http_code}' "$1" 2>/dev/null | grep -q "200"; }

log "=== ЗАПУСК RUMIX ALL ==="

RAM=$(free_mb)
for _ in $(seq 1 10); do
    [ -n "${RAM:-}" ] && [ "$RAM" -ge 800 ] 2>/dev/null && break
    sleep 1
    RAM=$(free_mb)
done

SKIP_SCANNER=0
if [ -n "${RAM:-}" ] && [ "$RAM" -lt 800 ] 2>/dev/null; then
    log "⚠️ Памяти мало (${RAM}MB) — Сканер пропускаю."
    SKIP_SCANNER=1
else
    log "✅ Память: ${RAM:-неизвестно}MB"
fi

for dir in "$ECO_DIR/rag" "$RUMIX_DIR/rag"; do
    if [ -f "$dir/indexer.py" ]; then
        log "🧠 Индексация RAG: $dir"
        ( cd "$dir" && python3 indexer.py ) || log "⚠️ Индексация не удалась — продолжаю."
        break
    fi
done

if http_ok "http://127.0.0.1:$NEON_PORT/v1/models"; then
    log "✅ Неон уже отвечает."
else
    NEON_SH=""
    for s in "$ECO_DIR/scripts/neon.sh" "$RUMIX_DIR/scripts/neon.sh"; do
        [ -f "$s" ] && { NEON_SH="$s"; break; }
    done
    if [ -n "$NEON_SH" ]; then
        log "🤖 Бужу Неона: $NEON_SH"
        bash "$NEON_SH" start
    else
        log "❌ neon.sh не найден."
    fi
    http_ok "http://127.0.0.1:$NEON_PORT/v1/models" && log "✅ Неон разбужен." \
        || log "⚠️ Неон не ответил."
fi

log "🌐 Запуск Shell..."
if bash "$SVC" start shell; then
    TOKEN=$(cat "$HOME/.rumix_token" 2>/dev/null)
    URL="http://127.0.0.1:$SHELL_PORT/"
    [ -n "$TOKEN" ] && URL="http://127.0.0.1:$SHELL_PORT/?t=$TOKEN"
    log "✅ Shell отвечает: $URL"
    if [ -n "$TOKEN" ]; then
        log "🔑 токен для APK: $TOKEN"
    else
        log "⚠️ токена нет — API будет отвечать 401"
    fi
else
    log "❌ Shell не поднялся. Лог: $ECO_DIR/logs/shell.log"
    URL="http://127.0.0.1:$SHELL_PORT/"
fi

if [ "$SKIP_SCANNER" = "1" ]; then
    log "⏭ CyberScanner пропущен."
else
    log "🛡️ Проверка CyberScanner..."
    bash "$SVC" start scanner
fi

log "=== RUMIX ГОТОВ ==="
command -v termux-open-url >/dev/null 2>&1 && termux-open-url "$URL"
exit 0
