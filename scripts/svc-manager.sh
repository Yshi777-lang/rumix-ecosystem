#!/data/data/com.termux/files/usr/bin/bash
# svc-manager.sh — диспетчер процессов дома.
# Главное правило: НИКОГДА не убивать по шаблону командной строки.

ECO_DIR="${RUMIX_ECO_DIR:-$HOME/rumix-ecosystem}"
RUMIX_DIR="${RUMIX_DATA_DIR:-$HOME/rumix}"
LOG_DIR="$ECO_DIR/logs"
RUN_DIR="$RUMIX_DIR/run"
SVDIR="${SVDIR:-$PREFIX/var/service}"
mkdir -p "$LOG_DIR" "$RUN_DIR"

log() { echo "[$(date '+%H:%M:%S')] $1"; }
pidfile() { echo "$RUN_DIR/$1.pid"; }

if [ -n "${RUMIX_SVC_MODE:-}" ]; then
    MODE="$RUMIX_SVC_MODE"
elif command -v sv >/dev/null 2>&1 && [ -d "$SVDIR" ]; then
    MODE="runit"
else
    MODE="nohup"
fi
export SVDIR

pid_of() {
    local f; f=$(pidfile "$1")
    [ -f "$f" ] || return 1
    cat "$f" 2>/dev/null
}

is_alive() {
    local p; p=$(pid_of "$1") || return 1
    [ -n "$p" ] && kill -0 "$p" 2>/dev/null
}

http_ok() {
    curl -s -o /dev/null -m 2 -w "%{http_code}" "$1" 2>/dev/null | grep -qE "20[0-9]"
}

wait_http() {
    local i=0 tries="${3:-10}"
    while [ "$i" -lt "$tries" ]; do
        if http_ok "$2"; then return 0; fi
        i=$((i + 1)); sleep 1
    done
    return 1
}

remember_pid() { echo "$2" > "$(pidfile "$1")"; }
forget_pid() { rm -f "$(pidfile "$1")"; }

install_service() {
    local name="$1" dir="$2" cmd="$3" logf="$4" svc="$SVDIR/$1"
    mkdir -p "$svc"
    cat > "$svc/run" <<EOF
#!/data/data/com.termux/files/usr/bin/sh
cd "$dir" || exit 1
exec $cmd >> "$logf" 2>&1
EOF
    chmod +x "$svc/run"
    log "🧩 runit-сервис '$name' → $svc/run"
}

do_install() {
    if [ "$MODE" != "runit" ]; then
        log "ℹ️ runit недоступен. Сервисы будут работать в nohup-режиме."
        return 0
    fi
    install_service shell "$ECO_DIR/backend" "python3 app.py" "$LOG_DIR/shell.log"
    log "✅ Готово."
}

start_shell() {
    log "🌐 Запуск Shell ($MODE)..."
    if [ "$MODE" = "runit" ] && [ -f "$SVDIR/shell/run" ]; then
        sv up shell || { log "❌ sv up shell не сработал"; return 1; }
    elif is_alive shell; then
        log "ℹ️ Shell уже жив (PID $(pid_of shell))."
        return 0
    else
        ( cd "$ECO_DIR/backend" || exit 1
          nohup python3 app.py >> "$LOG_DIR/shell.log" 2>&1 &
          echo $! > "$(pidfile shell)" )
    fi
    if wait_http shell "http://127.0.0.1:8001/api/agent/status" 15; then
        log "✅ Shell запущен."
    else
        log "❌ Shell не ответил. Лог: $LOG_DIR/shell.log"
        return 1
    fi
}

start_neon() {
    log "🤖 Запуск Неона..."
    local ns=""
    for s in "$ECO_DIR/scripts/neon.sh" "$RUMIX_DIR/scripts/neon.sh"; do
        [ -f "$s" ] && { ns="$s"; break; }
    done
    if [ -n "$ns" ]; then bash "$ns" start; else log "❌ Нет neon.sh."; return 1; fi
}

start_scanner() {
    log "🛡️ Запуск CyberScanner ($MODE)..."
    local dir=""
    [ -f "$RUMIX_DIR/archive/CyberScanner/web/app.py" ] && dir="$RUMIX_DIR/archive/CyberScanner"
    [ -z "$dir" ] && [ -f "$ECO_DIR/archive/CyberScanner/web/app.py" ] && dir="$ECO_DIR/archive/CyberScanner"
    if [ -z "$dir" ]; then log "⚠️ CyberScanner не найден."; return 1; fi
    ( cd "$dir" || exit 1
      nohup python3 web/app.py >> "$LOG_DIR/scanner.log" 2>&1 &
    scanner)" )
    log "✅ CyberScanner запущен."
}

stop_one() {
    local name="$1"
    if is_alive "$name"; then
        local p; p=$(pid_of "$name")
        kill -TERM "$p" 2>/dev/null
        forget_pid "$name"
        log "✅ $name остановлен."
    else
        log "⚠️ $name не был запущен."
    fi
}

stop_shell() { stop_one shell; }
stop_neon() { 
    if command -v sv >/dev/null 2>&1 && [ -d "$SVDIR/neon" ]; then sv down neon; 
    else local ns=""; for s in "$ECO_DIR/scripts/neon.sh" "$RUMIX_DIR/scripts/neon.sh"; do [ -f "$s" ] && { ns="$s"; break; }; done; [ -n "$ns" ] && bash "$ns" stop; fi
}
stop_scanner() { stop_one scanner; }

status() {
    echo "📊 СТАТУС ДОМА (режим: $MODE)"
    echo "───────────────────────────────"
    if http_ok "http://127.0.0.1:8001/api/agent/status"; then echo "  ✅ Shell — жив"; else echo "  ❌ Shell — спит"; fi
    if http_ok "http://127.0.0.1:8080/v1/models"; then echo "  ✅ Неон — жив"; else echo "  ❌ Неон — спит"; fi
    if is_alive scanner; then echo "  ✅ CyberScanner — жив"; else echo "  ❌ CyberScanner — спит"; fi
    echo "───────────────────────────────"
}

case "${1:-}" in
        echo "🔧 Запуск Forge (порт 5001)..."
        cd "$ECO_DIR/forge" || exit 1
        python3 app.py &
        echo $! > "$DATA_DIR/run/forge.pid"
        echo "✅ Forge запущен"
        ;;
    scanner) start_scanner;; all) start_neon; start_shell; start_scanner;; esac ;;
        echo "🔧 Запуск Forge (порт 5001)..."
        cd "$ECO_DIR/forge" || exit 1
        python3 app.py &
        echo $! > "$DATA_DIR/run/forge.pid"
        echo "✅ Forge запущен"
        ;;
    scanner) stop_scanner;; all) stop_shell; stop_neon; stop_scanner;; esac ;;
    install) do_install ;;
    status) status ;;
    *) echo "Использование: $0 {start|stop|install|status} [shell|neon|scanner|all]" ;;
esac
