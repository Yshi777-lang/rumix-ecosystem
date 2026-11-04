#!/data/data/com.termux/files/usr/bin/bash

RUMIX_DIR="$HOME/rumix"
ECO_DIR="$HOME/rumix-ecosystem"
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

# Ждём, пока память освободится (макс 10 сек)
log "💤 Ожидание освобождения памяти..."
for i in {1..10}; do
  FREE_MB=$(free -m | awk '/Mem:/ {print $7}')
  if [ "$FREE_MB" -gt 800 ]; then
    log "✅ Память свободна (${FREE_MB}MB)."
    break
  fi
  sleep 1
done

if [ "$FREE_MB" -le 800 ]; then
  log "⚠️ Памяти всё ещё мало (${FREE_MB}MB). Возможны сбои."
fi

# 1. Память (не убиваем скрипт, если не вышло)
log "🧠 Подготовка памяти..."
if [ -d "$RUMIX_DIR/rag" ]; then
  cd "$RUMIX_DIR/rag" && python indexer.py || log "⚠️ Ошибка индексации (продолжаем)."
fi

# 2. Неон (проверяем, если спит — будим)
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
  log "⚠️ Неон спит. Бужу..."
  if [ -f "$RUMIX_DIR/scripts/neon.sh" ]; then
    bash "$RUMIX_DIR/scripts/neon.sh" start
    sleep 5
    if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:$NEON_PORT/v1/models | grep -q "200"; then
      log "✅ Неон разбужен."
      NEON_OK=1
    else
      log "❌ Неон не проснулся."
    fi
  else
    log "❌ neon.sh не найден, не могу разбудить."
  fi
fi

# 3. Shell (8001) — через svc-manager
log "🌐 Запуск Shell (через svc-manager)..."
bash "$ECO_DIR/scripts/svc-manager.sh" start shell
sleep 2
if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:$FLASK_PORT/api/status | grep -q "200"; then
  log "✅ Backend отвечает."
  termux-open-url http://127.0.0.1:$FLASK_PORT
else
  log "❌ Backend не отвечает."
fi

# 4. CyberScanner (8002) — через svc-manager (если есть)
log "🛡️ Проверка CyberScanner..."
bash "$ECO_DIR/scripts/svc-manager.sh" start scanner

log "=== RUMIX ГОТОВ ==="
