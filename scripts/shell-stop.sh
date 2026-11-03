#!/data/data/com.termux/files/usr/bin/bash
# shell-stop.sh — остановка Rumix Shell

KILLED=0
if pkill -f "python3 app.py" 2>/dev/null; then KILLED=1; fi
if pkill -f "python app.py" 2>/dev/null; then KILLED=1; fi

if [ "$KILLED" -eq 1 ]; then
    echo "✅ Rumix Shell остановлен."
else
    echo "⚠️ Rumix Shell не был запущен."
fi
