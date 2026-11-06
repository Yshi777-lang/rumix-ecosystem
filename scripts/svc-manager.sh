#!/data/data/com.termux/files/usr/bin/bash
ECO_DIR="${RUMIX_ECO_DIR:-$HOME/rumix-ecosystem}"
RUMIX_DIR="${RUMIX_DATA_DIR:-$HOME/rumix}"
LOG_DIR="$ECO_DIR/logs"
RUN_DIR="$RUMIX_DIR/run"
SVDIR="${SVDIR:-$PREFIX/var/service}"
mkdir -p "$LOG_DIR" "$RUN_DIR"

pidfile() { echo "$RUN_DIR/$1.pid"; }
is_alive() { local p=$(cat "$(pidfile "$1")" 2>/dev/null); [ -n "$p" ] && kill -0 "$p" 2>/dev/null; }

start_service() {
    local name="$1" dir="$2" logf="$3"; shift 3
    if is_alive "$name"; then echo "ℹ️ $name уже жив."; return 0; fi
    ( cd "$dir" || exit 1; nohup "$@" >> "$logf" 2>&1 & echo $! > "$(pidfile "$name")" )
    echo "✅ $name запущен."
}

stop_one() {
    local name="$1" p=$(cat "$(pidfile "$name")" 2>/dev/null)
    if [ -n "$p" ] && kill -0 "$p" 2>/dev/null; then
        kill -TERM "$p" 2>/dev/null; sleep 1; kill -KILL "$p" 2>/dev/null || true
        rm -f "$(pidfile "$name")"; echo "✅ $name остановлен."
    else
        echo "ℹ️ $name не был запущен."
    fi
}

case "${1:-}" in
    start)
        case "${2:-}" in
            shell) start_service shell "$ECO_DIR/backend" "$LOG_DIR/shell.log" python3 app.py ;;
            forge) start_service forge "$ECO_DIR/forge" "$LOG_DIR/forge.log" python3 app.py ;;
            *) echo "Использование: $0 start {shell|forge}" ;;
        esac ;;
    stop)
        case "${2:-}" in
            shell|forge) stop_one "$2" ;;
            *) echo "Использование: $0 stop {shell|forge}" ;;
        esac ;;
    status)
        echo "📊 СТАТУС:"
        is_alive shell && echo "  ✅ Shell" || echo "  ❌ Shell"
        is_alive forge && echo "  ✅ Forge" || echo "  ❌ Forge" ;;
    *) echo "Использование: $0 {start|stop|status} {shell|forge}" ;;
esac
