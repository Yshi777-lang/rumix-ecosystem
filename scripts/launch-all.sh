#!/data/data/com.termux/files/usr/bin/bash

RUMIX_DIR="$HOME/rumix"
WORK_DIR="$HOME/Work"
FLASK_PORT=8001
NEON_PORT=8080
SCANNER_PORT=8002
LOG_FILE="$RUMIX_DIR/logs/shell.log"

mkdir -p "$RUMIX_DIR/logs"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=== ЗАПУСК RUMIX ALL ==="

# 1. Память (не убиваем скрипт, если не вышло)
log "🧠 Подготовка памяти..."
if [ -d "$RUMIX_DIR/rag" ]; then
  cd "$RUMIX_DIR/rag" && python indexer.py || log "⚠️ Ошибка индексации (продолжаем)."
fi

# 2. Неон (ждём до 10 секунд)
log "🤖 Проверка Неона..."
NEON_OK=0
for i in {1..10}; do
  if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:$NEON_PORT/v1/models | grep -q "200"; then
    NEON_OK=1
    log "✅ Неон отвечает."
    break
  fi
  sleep 1
done
if [ $NEON_OK -eq 0 ]; then
  log "⚠️ Неон не отвечает после 10 сек."
fi

# 3. Shell (8001)
log "🌐 Запуск Rumix Shell..."
pkill -f "python3 app.py" 2>/dev/null
sleep 1
cd "$RUMIX_DIR/backend"
nohup python app.py > "$LOG_FILE" 2>&1 &
SHELL_PID=$!
log "✅ Shell запущен (PID: $SHELL_PID)."
sleep 3
if curl -s -o /dev/null -o
w "%{http_code}" http://127.0.0.1:$FLASK_PORT/api/status | grep -q "200"; then
  log "✅ Backend отвечает."
  termux-open-url http://127.0.0.1:$FLASK_PORT
else
  log "❌ Backend не отвечает."
fi

# 4. CyberScanner (8002)
if [ -f "$WORK_DIR/archive/CyberScanner/web/app.py" ]; then
  log "🛡️ Запуск CyberScanner..."
  cd "$WORK_DIR/archive/CyberScanner"
  nohup python3 web/app.py > scanner.log 2>&1 &
  log "✅ CyberScanner запущен (PID: $!)."
else
  log "⚠️ CyberScanner не найден."
fi

log "=== RUMIX ГОТОВ ==="
