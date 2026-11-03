#!/data/data/com.termux/files/usr/bin/bash
# recon.sh — тихая DNS-разведка
# Фурия 🦊 — свидетель. Тихая. Без SYN. Без шума.
# Исправлено: проверяем не только код возврата, но и текст вывода.

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

# Перенаправляем весь вывод (stdout+stderr) в лог и на экран одновременно
exec > >(tee "$LOG") 2>&1

echo "═══════════════════════════════════════════════"
echo "🔍 RECON: $TARGET"
echo "📅 Дата: $DATE"
echo "🦊 Фурия — тихая разведка"
echo "═══════════════════════════════════════════════"
echo ""

# Функция проверки вывода nslookup
check_nslookup() {
    local out="$1"
    local label="$2"
    if echo "$out" | grep -qE "Can't find|No answer|NXDOMAIN"; then
        ERRORS=$((ERRORS+1))
        echo "❌ Ошибка: $label"
    fi
}

# 1. Базовый IP
echo "─── 1. Базовый IP (системный резолвер) ───"
OUT=$(nslookup "$TARGET" 2>&1); echo "$OUT"
check_nslookup "$OUT" "базовый IP"
echo ""

# 2. Сравнение резолверов
echo "─── 2. Сравнение резолверов ───"
for ns in 8.8.8.8 1.1.1.1 9.9.9.9; do
    echo "=== $ns ==="
    OUT=$(nslookup "$TARGET" "$ns" 2>&1); echo "$OUT"
    check_nslookup "$OUT" "резолвер $ns"
    echo ""
done

# 3-7. Записи (MX, NS, TXT, SOA, ANY)
for type in MX NS TXT SOA ANY; do
    echo "─── $type-записи ───"
    OUT=$(nslookup -type="$type" "$TARGET" 2>&1); echo "$OUT"
    check_nslookup "$OUT" "$type"
    echo ""
done

echo "═══════════════════════════════════════════════"
echo "✅ Разведка завершена"
echo "📝 Лог: $LOG"
echo "═══════════════════════════════════════════════"

echo ""
if [ "$ERRORS" -eq 0 ]; then
  echo "🦊 Фурия: периметр чист. Тихая разведка завершена."
else
  echo "🦊 Фурия: ⚠️ разведка завершена с $ERRORS ошибками. Проверь лог: $LOG"
fi
