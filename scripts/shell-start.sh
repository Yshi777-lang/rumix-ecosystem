#!/data/data/com.termux/files/usr/bin/bash
# shell-start.sh — запуск Rumix Shell.
# Делегирует svc-manager.sh: адресация по имени сервиса (runit или PID-файл),
# а не `pkill -f "python3 app.py"`, который заодно убивал CyberScanner и чужой Flask.

echo "🌊 Rumix Shell — запуск..."
ECO_DIR="${RUMIX_ECO_DIR:-$HOME/rumix-ecosystem}"
SVC="$ECO_DIR/scripts/svc-manager.sh"

if [ ! -f "$SVC" ]; then
    echo "❌ Не найден $SVC"
    exit 1
fi

# Перезапуск: стоп по имени сервиса, затем старт.
bash "$SVC" stop shell >/dev/null 2>&1

if ! bash "$SVC" start shell; then
    echo "   ❌ Shell не поднялся. Логи: $ECO_DIR/logs/shell.log"
    exit 1
fi

# Токен установки: без него /api/* отвечает 401. Он же нужен APK.
TOKEN=$(cat "$HOME/.rumix_token" 2>/dev/null)
URL="http://127.0.0.1:8001/"
[ -n "$TOKEN" ] && URL="http://127.0.0.1:8001/?t=$TOKEN"

echo "   🌐 $URL"
if [ -n "$TOKEN" ]; then
    echo "   🔑 токен для APK: $TOKEN"
else
    echo "   ⚠️ токен не найден (~/.rumix_token) — API будет отвечать 401"
fi

command -v termux-open-url >/dev/null 2>&1 && termux-open-url "$URL"
