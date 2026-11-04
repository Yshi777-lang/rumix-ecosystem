#!/data/data/com.termux/files/usr/bin/bash
# fury-light.sh — облегчённая версия Фурии для API (без pkg/apt/pip).

echo "🦊 AI FURY (Light) — Аудит периметра"
echo "════════════════════════════════════"

echo ""
echo "💾 ДИСК"
df -h /data/data/com.termux/files/home 2>/dev/null | head -2

echo ""
echo "🧠 ПАМЯТЬ"
free -m 2>/dev/null | awk '/Mem:/ {print "  Всего: " $2 " MB, Свободно: " $7 " MB"}'

echo ""
echo "🌐 ПОРТЫ (проверка через процессы)"
# 8001 — Shell (python3 app.py)
if pgrep -f "python3 app.py" > /dev/null || pgrep -f "python app.py" > /dev/null; then
    echo "  ✅ 8001 (Shell) — процесс жив"
else
    echo "  ⚠️  8001 (Shell) — не запущен"
fi
# 8080 — Неон (llama-server)
if pgrep -f "llama-server" > /dev/null; then
    echo "  ✅ 8080 (Неон) — процесс жив"
else
    echo "  ⚠️  8080 (Неон) — не запущен"
fi
# 8002 — CyberScanner
if pgrep -f "web/app.py" > /dev/null; then
    echo "  ✅ 8002 (CyberScanner) — процесс жив"
else
    echo "  ⚠️  8002 (CyberScanner) — не запущен"
fi

echo ""
echo "🤖 НЕОН (llama-server)"
if pgrep -f "llama-server" > /dev/null; then
    echo "  ✅ Неон жив"
else
    echo "  ⚠️  Неон спит"
fi

echo ""
echo "════════════════════════════════════"
echo "🦊 Лёгкий аудит завершён."
