#!/data/data/com.termux/files/usr/bin/bash
set -e

RUMIX_DIR="$HOME/rumix"
WORK_DIR="$HOME/Work"
FLASK_PORT=8001
NEON_PORT=8080
LOG_FILE="$RUMIX_DIR/logs/shell.log"

mkdir -p "$RUMIX_DIR/logs"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=== ЗАПУСК RUMIX ALL ==="

if ! command -v python3 &> /dev/null; then
  log "❌ Python не найден."
  exit 1
fi

log "🧠 Подготовка памяти..."
cd "$RUMIX_DIR/rag"
python indexer.py || { log "❌ Ошибка индексации."; exit 1; }

log "🤖 Проверка Неона..."
if ! curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:$NEON_PORT/v1/models | grep -q "200"; then
  log "⚠️ Неон не отвечает."
fi

log "🌐 Запуск Rumix Shell..."
cd "$RUMIX_DIR/backend"
nohup python app.py > "$LOG_FILE" 2>&1 &
SHELL_PID=$!
log "✅ Shell запущен (PID: $SHELL_PID)."

sleep 3
if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:$FLASK_PORT/api/status | grep -q "200"; then
  log "✅ Backend отвечает."
  termux-open-url http://127.0.0.1:$FLASK_PORT
else
  log "❌ Backend не отвечает."
fi

log "=== RUMIX ГОТОВ ==="
