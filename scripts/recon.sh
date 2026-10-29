#!/data/data/com.termux/files/usr/bin/bash
# ═══════════════════════════════════════════════════════
# recon.sh — тихая DNS-разведка
# Фурия 🦊 — свидетель. Тихая. Без SYN. Без шума.
# ═══════════════════════════════════════════════════════

# Проверка аргумента
if [ -z "$1" ]; then
    echo "🦊 recon.sh — тихая DNS-разведка"
    echo ""
    echo "Использование: recon.sh <domain>"
    echo ""
    echo "Пример: recon.sh github.com"
    exit 1
fi

TARGET="$1"
DATE=$(date +%Y-%m-%d_%H-%M)
LOG_DIR="$HOME/rumix/logs"
ERRORS=0
LOG="$LOG_DIR/recon-${TARGET}-${DATE}.log"

mkdir -p "$LOG_DIR"

# Начало
{
echo "═══════════════════════════════════════════════"
echo "🔍 RECON: $TARGET"
echo "📅 Дата: $DATE"
echo "🦊 Фурия — тихая разведка"
echo "═══════════════════════════════════════════════"
echo ""

# 1. Базовый IP через системный резолвер
echo "─── 1. Базовый IP (системный резолвер) ───"
nslookup "$TARGET" 2>&1; [ $? -ne 0 ] && ERRORS=$((ERRORS+1))
echo ""

# 2. Сравнение резолверов
echo "─── 2. Сравнение резолверов ───"
for ns in 8.8.8.8 1.1.1.1 9.9.9.9; do
    echo "=== $ns ==="
    nslookup "$TARGET" "$ns" 2>&1; [ $? -ne 0 ] && ERRORS=$((ERRORS+1))
    echo ""
done

# 3. MX-записи
echo "─── 3. MX-записи (почтовые серверы) ───"
nslookup -type=MX "$TARGET" 2>&1; [ $? -ne 0 ] && ERRORS=$((ERRORS+1))
echo ""

# 4. NS-записи
echo "─── 4. NS-записи (DNS-зона) ───"
nslookup -type=NS "$TARGET" 2>&1; [ $? -ne 0 ] && ERRORS=$((ERRORS+1))
echo ""

# 5. TXT-записи (SPF, DKIM, проверки)
echo "─── 5. TXT-записи (SPF, верификация) ───"
nslookup -type=TXT "$TARGET" 2>&1; [ $? -ne 0 ] && ERRORS=$((ERRORS+1))
echo ""

# 6. SOA-запись
echo "─── 6. SOA-запись (authoritative info) ───"
nslookup -type=SOA "$TARGET" 2>&1; [ $? -ne 0 ] && ERRORS=$((ERRORS+1))
echo ""

# 7. ANY (всё что отдаст сервер)
echo "─── 7. ANY (все записи) ───"
nslookup -type=ANY "$TARGET" 2>&1; [ $? -ne 0 ] && ERRORS=$((ERRORS+1))
echo ""

# Финал
echo "═══════════════════════════════════════════════"
echo "✅ Разведка завершена"
echo "📝 Лог: $LOG"
echo "═══════════════════════════════════════════════"

} | tee "$LOG"

echo ""
if [ "$ERRORS" -eq 0 ]; then
  echo "🦊 Фурия: периметр чист. Тихая разведка завершена."
else
  echo "🦊 Фурия: ⚠️ разведка завершена с $ERRORS ошибками. Проверь лог: $LOG"
fi
