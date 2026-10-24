#!/data/data/com.termux/files/usr/bin/bash
# shell-stop.sh — остановка Rumix Shell
# Создано: 19.10.2026 (Тиамат + Зая)

pkill -f "python3 app.py" 2>/dev/null
echo "✅ Rumix Shell остановлен."
