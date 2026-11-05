#!/data/data/com.termux/files/usr/bin/bash
# stop-all.sh — остановка дома.
# Остановка идёт по именам сервисов через svc-manager (без pkill).

ECO_DIR="${RUMIX_ECO_DIR:-$HOME/rumix-ecosystem}"
SVC="$ECO_DIR/scripts/svc-manager.sh"

echo "🛑 Остановка Rumix..."

if [ ! -f "$SVC" ]; then
    echo "  ❌ не найден $SVC"
    exit 1
fi

bash "$SVC" stop all
command -v termux-wake-unlock >/dev/null 2>&1 && termux-wake-unlock

echo "🏁 Дом спит."
