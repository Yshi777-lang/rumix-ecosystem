#!/data/data/com.termux/files/usr/bin/bash
# stop-all.sh — остановка дома

echo "🛑 Остановка Rumix..."

# Shell (Flask)
if pkill -f "python.*app.py" 2>/dev/null; then
    echo "  ✅ Shell остановлен"
else
    echo "  ⚠️ Shell не был запущен"
fi

# CyberScanner
if pkill -f "CyberScanner.*web/app.py" 2>/dev/null; then
    echo "  ✅ CyberScanner остановлен"
else
    echo "  ⚠️ Сканер не был запущен"
fi

# Неон (через sv, если есть, или напрямую)
NEON_KILLED=0
if command -v sv &> /dev/null; then
    export SVDIR=$PREFIX/var/service
    if sv down neon 2>/dev/null; then NEON_KILLED=1; fi
fi

if [ "$NEON_KILLED" -eq 0 ]; then
    if pkill -f "llama-server" 2>/dev/null; then
        echo "  ✅ Неон остановлен (напрямую)"
    else
        echo "  ⚠️ Неон не был запущен"
    fi
else
    echo "  ✅ Неон остановлен (через sv)"
fi

echo "🏁 Дом спит."
