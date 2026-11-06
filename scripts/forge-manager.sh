#!/data/data/com.termux/files/usr/bin/bash
# forge-manager.sh — управление сервисом Prompt Forge

ECO_DIR="$HOME/rumix-ecosystem"
DATA_DIR="$HOME/rumix"
ACTION="$1"

case "$ACTION" in
    start)
        echo "🔧 Запуск Forge (порт 5001)..."
        mkdir -p "$DATA_DIR/logs" "$DATA_DIR/run"
        cd "$ECO_DIR/forge" || exit 1
        python3 app.py > "$DATA_DIR/logs/forge.log" 2>&1 &
        echo $! > "$DATA_DIR/run/forge.pid"
        echo "✅ Forge запущен. Логи: $DATA_DIR/logs/forge.log"
        ;;
    stop)
        echo "🛑 Остановка Forge..."
        if [ -f "$DATA_DIR/run/forge.pid" ]; then
            kill $(cat "$DATA_DIR/run/forge.pid") 2>/dev/null
            rm -f "$DATA_DIR/run/forge.pid"
            echo "✅ Forge остановлен"
        else
            pkill -f "python3.*app.py" 2>/dev/null
            echo "✅ Forge остановлен (принудительно)"
        fi
        ;;
    status)
        if [ -f "$DATA_DIR/run/forge.pid" ] && kill -0 $(cat "$DATA_DIR/run/forge.pid") 2>/dev/null; then
            echo "✅ Forge работает (PID: $(cat "$DATA_DIR/run/forge.pid"))"
        else
            echo "❌ Forge не работает"
        fi
        ;;
    *)
        echo "Использование: $0 {start|stop|status}"
        exit 1
        ;;
esac
