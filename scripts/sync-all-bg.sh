#!/data/data/com.termux/files/usr/bin/bash
# sync-all-bg.sh — запускает sync-all.sh в фоне, не блокируя Flask

LOG="$HOME/rumix/logs/sync-all.log"
mkdir -p "$(dirname "$LOG")"

echo "[$(date)] Запуск синхронизации в фоне..." >> "$LOG"
nohup bash ~/rumix/scripts/sync-all.sh >> "$LOG" 2>&1 &
echo "✅ Синхронизация запущена в фоне. Лог: $LOG"
