#!/data/data/com.termux/files/usr/bin/bash
# stop-all.sh — остановка дома

echo "🛑 Остановка Rumix..."

# Shell (Flask)
pkill -f "python3 app.py" 2>/dev/null && echo "  ✅ Shell остановлен" || echo "  ⚠️ Shell не был запущен"

# CyberScanner
pkill -f "web/app.py" 2>/dev/null && echo "  ✅ CyberScanner остановлен" || echo "  ⚠️ Сканер не был запущен"

# Неон
if command -v sv &> /dev/null; then
    export SVDIR=$PREFIX/var/service
    sv down neon 2>/dev/null && echo "  ✅ Неон остановлен" || echo "  ⚠️ Неон не был запущен"
fi

echo "🏁 Дом спит."
