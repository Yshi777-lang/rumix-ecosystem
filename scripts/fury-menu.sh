#!/data/data/com.termux/files/usr/bin/bash
# fury-menu.sh — подменю Фурии 🦊

while true; do
    clear
    gum style --border normal --padding "0 2" --border-foreground 208 "🦊 ФУРИЯ — ПОДМЕНЮ"

    choice=$(gum choose \
        "🔍 Аудит периметра (fury-light.sh)" \
        "🌐 Recon DNS (recon.sh)" \
        "📦 Обновить pip-пакеты" \
        "🔙 Назад в Rumix" \
        "🚪 Выход")

    case "$choice" in
        "🔍 Аудит периметра (fury-light.sh)")
            bash "$HOME/rumix-ecosystem/scripts/fury-light.sh"
            echo ""; read -p "Enter для возврата..."
            ;;
        "🌐 Recon DNS (recon.sh)")
            echo ""
            read -p "Введи домен (например github.com): " domain
            if [ -n "$domain" ]; then
                bash "$HOME/rumix-ecosystem/scripts/recon.sh" "$domain"
            else
                echo "⚠️  Домен не введён."
            fi
            echo ""; read -p "Enter для возврата..."
            ;;
        "📦 Обновить pip-пакеты")
            echo ""
            bash "$HOME/rumix-ecosystem/scripts/fury-light.sh" --pip-update
            echo ""; read -p "Enter для возврата..."
            ;;
        "🔙 Назад в Rumix") exit 0 ;;
        "🚪 Выход") echo "🦊 До встречи, папа."; exit 0 ;;
    esac
done
