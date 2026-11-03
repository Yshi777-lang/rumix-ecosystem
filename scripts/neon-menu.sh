#!/data/data/com.termux/files/usr/bin/bash
# neon-menu.sh — подменю Неона 🤖

while true; do
    clear
    gum style --border normal --padding "0 2" --border-foreground 93 "🤖 НЕОН — ПОДМЕНЮ"

    choice=$(gum choose \
        "💬 Чат с Неоном" \
        "🎭 Редактор характера" \
        "🔙 Назад в Rumix" \
        "🚪 Выход")

    case "$choice" in
        "💬 Чат с Неоном")
            bash "$HOME/rumix/scripts/neon-chat.sh"
            echo ""; read -p "Enter..."
            ;;
        "🎭 Редактор характера")
            bash "$HOME/rumix/scripts/neon-character.sh"
            ;;
        "🔙 Назад в Rumix") exit 0 ;;
        "🚪 Выход") echo "🤖 До встречи, папа."; exit 0 ;;
    esac
done
