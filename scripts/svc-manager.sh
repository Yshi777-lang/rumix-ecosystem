#!/data/data/com.termux/files/usr/bin/bash
# svc-manager.sh — диспетчер процессов дома.

ECO_DIR="$HOME/rumix-ecosystem"
RUMIX_DIR="$HOME/rumix"
LOG_DIR="$ECO_DIR/logs"
mkdir -p "$LOG_DIR"

log() { echo "[$(date '+%H:%M:%S')] $1"; }

start_shell() {
    log "🌐 Запуск Shell..."
    pkill -f "python3 app.py" 2>/dev/null || true
    pkill -f "python app.py" 2>/dev/null || true
    sleep 1
    cd "$ECO_DIR/backend" || return 1
    nohup python3 app.py >> "$LOG_DIR/shell.log" 2>&1 &
    sleep 2
    if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8001/api/status | grep -q "200"; then
        log "✅ Shell запущен (PID: $!)."
    else
        log "❌ Shell не ответил."
    fi
}

start_neon() {
    log "🤖 Запуск Неона через runit..."
    export SVDIR="$PREFIX/var/service"
    sv up neon 2>/dev/null
    sleep 3
    if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8080/v1/models | grep -q "200"; then
        log "✅ Неон жив."
    else
        log "❌ Неон не ответил."
    fi
}

start_scanner() {
    log "🛡️ Запуск CyberScanner..."
    pkill -f "CyberScanner.*web/app.py" 2>/dev/null || true
    sleep 1
    if [ -f "$RUMIX_DIR/archive/CyberScanner/web/app.py" ]; then
        cd "$RUMIX_DIR/archive/CyberScanner"
        nohup python3 web/app.py >> "$LOG_DIR/scanner.log" 2>&1 &
        log "✅ CyberScanner запущен (PID: $!)."
    elif [ -f "$ECO_DIR/archive/CyberScanner/web/app.py" ]; then
         cd "$ECO_DIR/archive/CyberScanner"
         nohup python3 web/app.py >> "$LOG_DIR/scanner.log" 2>&1 &
         log "✅ CyberScanner запущен (PID: $!)."
    else
        log "⚠️ CyberScanner не найден."
    fi
}

stop_shell() {
    log "⏹ Остановка Shell..."
    pkill -f "python.*app.py" 2>/dev/null && log "✅ Shell остановлен." || log "⚠️ Shell не был запущен."
}

stop_neon() {
    log "⏹ Остановка Неона..."
    export SVDIR="$PREFIX/var/service"
    sv down neon 2>/dev/null && log "✅ Неон остановлен." || log "⚠️ Неон не был запущен."
}

stop_scanner() {
    log "⏹ Остановка CyberScanner..."
    pkill -f "CyberScanner.*web/app.py" 2>/dev/null && log "✅ CyberScanner остановлен." || log "⚠️ CyberScanner не был запущен."
}

status() {
    echo "📊 СТАТУС ДОМА"
    echo "───────────────────────────────"
    if pgrep -f "python.*app.py" > /dev/null; then echo "  ✅ Shell (8001) — жив"; else echo "  ❌ Shell (8001) — спит"; fi
    if pgrep -f "llama-server" > /dev/null; then echo "  ✅ Неон (8080) — жив"; else echo "  ❌ Неон (8080) — спит"; fi
    if pgrep -f "CyberScanner.*web/app.py" > /dev/null; then echo "  ✅ CyberScanner (8002) — жив"; else echo "  ❌ CyberScanner (8002) — спит"; fi
    echo "───────────────────────────────"
}

case "$1" in
    start)
        case "$2" in
            shell) start_shell ;;
            neon) start_neon ;;
            scanner) start_scanner ;;
            all) start_neon; start_shell; start_scanner ;;
            *) echo "Использование: $0 start {shell|neon|scanner|all}" ;;
        esac
        ;;
    stop)
        case "$2" in
            shell) stop_shell ;;
            neon) stop_neon ;;
            scanner) stop_scanner ;;
            all) stop_shell; stop_neon; stop_scanner ;;
            *) echo "Использование: $0 stop {shell|neon|scanner|all}" ;;
        esac
        ;;
    status) status ;;
    *) echo "Использование: $0 {start|stop|status} [shell|neon|scanner|all]" ;;
esac
