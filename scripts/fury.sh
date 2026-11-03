#!/data/data/com.termux/files/usr/bin/bash
# AI Fury v1.1 — Аудит периметра (с мостом)
# Неоновый шёпот. Фурия 🦊

# === Флаг --pip-update: обновление pip-пакетов ===
if [ "$1" = "--pip-update" ]; then
    echo "📦 Обновление устаревших pip-пакетов..."
    echo ""

    outdated=$(timeout 20 pip list --outdated 2>/dev/null | awk 'NR>2 {print $1}')

    if [ -z "$outdated" ]; then
        echo "✅ Все pip-пакеты обновлены."
        exit 0
    fi

    echo "Найдены устаревшие пакеты:"
    echo "$outdated" | sed 's/^/   /'
    echo ""

    read -p "Обновить все? (y/n): " confirm
    if [ "$confirm" != "y" ]; then
        echo "⚠️  Отменено."
        exit 0
    fi

    echo ""
    echo "$outdated" | while IFS= read -r pkg; do
        echo "⬆️  $pkg..."
        pip install --upgrade "$pkg" 2>&1 | tail -1
    done

    echo ""
    echo "✅ Обновление завершено."
    exit 0
fi
# === Конец флага ===



LOG="$HOME/rumix/logs/fury.log"
echo "=== Fury $(date '+%Y-%m-%d %H:%M') ===" >> "$LOG"

# --- МОСТ: сюда добавляй новые модули ---
fury_module_disk() {
    echo "💾 ДИСК (наш дом)"
    df -h /data/data/com.termux/files/home 2>/dev/null | head -3
}

fury_module_memory() {
    echo "🧠 ПАМЯТЬ"
    free -h 2>/dev/null | head -3
}

fury_module_ports() {
    echo "🌐 ПОРТЫ (проверка ключевых)"
    # В Termux netstat не работает для TCP, проверяем через curl
    if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8001/api/status 2>/dev/null | grep -q "200"; then
        echo "  ✅ 8001 (Shell) отвечает"
    else
        echo "  ⚠️  8001 (Shell) не отвечает"
    fi
    if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8080/v1/models 2>/dev/null | grep -q "200"; then
        echo "  ✅ 8080 (Неон) отвечает"
    else
        echo "  ⚠️  8080 (Неон) не отвечает"
    fi
    if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8002 2>/dev/null | grep -qE "200|302"; then
        echo "  ✅ 8002 (CyberScanner) отвечает"
    else
        echo "  ⚠️  8002 (CyberScanner) не отвечает"
    fi
}

fury_module_gnomik() {
    echo "🤖 НЕОН (llama-server)"
    if pgrep -f "llama-server" > /dev/null; then
        PID=$(pgrep -f llama-server | head -1)
        echo "  ✅ Неон жив (PID: $PID)"
        curl -s http://127.0.0.1:8080/v1/models > /dev/null 2>&1 && echo "  ✅ Порт 8080 отвечает"
    else
        echo "  ⚠️  Неон не запущен"
    fi
}
# --- КОНЕЦ МОСТА ---

echo "🦊 AI FURY v1.1 — Аудит периметра"
echo "════════════════════════════════════"

echo ""
echo "📦 ПАКЕТЫ"
pkg update -y > /dev/null 2>&1 || true
pkg upgrade -y > /dev/null 2>&1 || true
echo "  ✅ pkg — готово"
apt update -y > /dev/null 2>&1 || true
apt upgrade -y > /dev/null 2>&1 || true
echo "  ✅ apt — готово"
echo "  → pip (устаревшие):"
pip list --outdated 2>/dev/null | head -8 || true

echo ""; fury_module_disk
echo ""; fury_module_memory
echo ""; fury_module_ports
echo ""; fury_module_gnomik

echo ""
echo "════════════════════════════════════"
echo "🦊 Аудит завершён. Лог: ~/rumix/logs/fury.log"
echo "Fury OK" >> "$LOG"
