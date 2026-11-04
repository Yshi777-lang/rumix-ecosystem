#!/data/data/com.termux/files/usr/bin/bash
# sync-menu.sh — меню управления синхронизацией
while true; do
    clear
    echo "🔄 УПРАВЛЕНИЕ СИНХРОНИЗАЦИЕЙ"
    bash ~/rumix-ecosystem/scripts/sync-control.sh status
    choice=$(gum choose --height 10 "▶️ Запустить" "⏹ Остановить" "⏱ Интервал" "⚡ Сейчас" "⬅️ Назад")
    case "$choice" in
        "▶️ Запустить") bash ~/rumix-ecosystem/scripts/sync-control.sh start; read -p "Enter..." ;;
        "⏹ Остановить") bash ~/rumix-ecosystem/scripts/sync-control.sh stop; read -p "Enter..." ;;
        "⏱ Интервал") read -p "Минуты: " i; bash ~/rumix-ecosystem/scripts/sync-control.sh interval "$i"; read -p "Enter..." ;;
        "⚡ Сейчас") bash ~/rumix-ecosystem/scripts/sync-control.sh now; read -p "Enter..." ;;
        *) break ;;
    esac
done
