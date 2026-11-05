#!/data/data/com.termux/files/usr/bin/bash
# shell-stop.sh — остановка Rumix Shell.
# Останавливаем только Shell: `pkill -f "python.*app.py"` задевал ещё и CyberScanner.

ECO_DIR="${RUMIX_ECO_DIR:-$HOME/rumix-ecosystem}"
SVC="$ECO_DIR/scripts/svc-manager.sh"

if [ ! -f "$SVC" ]; then
    echo "❌ не найден $SVC"
    exit 1
fi

bash "$SVC" stop shell
