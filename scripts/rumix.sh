#!/data/data/com.termux/files/usr/bin/bash
# rumix.sh — главное меню дома 🧬

# Проверка PIN (если установлен)
if [ -f "$HOME/rumix/scripts/rumix-pin.sh" ]; then
    if ! bash "$HOME/rumix/scripts/rumix-pin.sh" check; then
        exit 1
    fi
fi

while true; do
    clear
    gum style --border double --padding "1 2" --border-foreground 93 "🧬 RUMIX — НЕОНОВЫЙ ШЁПОТ"

    # Метрики устройства (быстро, без LLM)
    STORAGE=$(df -h ~ 2>/dev/null | awk 'NR==2 {print $4}')
    RAM_AVAIL=$(free -m 2>/dev/null | awk 'NR==2 {print $7}')  # available, не free
    BATTERY=$(termux-battery-status 2>/dev/null | grep percentage | awk -F': ' '{print $2}' | tr -d ',')
    if ping -c 1 -W 1 8.8.8.8 >/dev/null 2>&1; then
        NET="Online"
    else
        NET="Offline"
    fi

    echo "  💾 ${STORAGE:-?}   🧠 ${RAM_AVAIL:-?} MB   🔋 ${BATTERY:-?}%   🌐 ${NET}"
    echo ""

    choice=$(gum choose --height 20 \
        "🌊 Оболочка (запуск всего)" \
        "🔄 Синхронизация (GitHub)" \
        "💻 Terminal (zsh)" \
        "🤖 AI: Неон (меню)" \
        "🤖 Agent Runtime" \
        "🦊 AI: Фурия (меню)" \
        "📦 Установить Неона" \
        "🌿 Git: Work" \
        "🌊 Rumix Shell" \
        "📁 Проекты" \
        "🗂  Файлы" \
        "🐙 GitHub" \
        "⚙️  Настройки и память" \
        "📖 Инструкция" \
        "🚪 Выход")

    case "$choice" in
        "🔄 Синхронизация (GitHub)")
            bash "$HOME/rumix/scripts/sync-menu.sh"
            echo ""
            read -p "Нажми Enter..."
            ;;
        "🌊 Оболочка (запуск всего)")
            bash "$HOME/rumix/scripts/launch-all.sh"
            echo ""
            read -p "Нажми Enter..."
            ;;
        "💻 Terminal (zsh)")
            exec zsh
            ;;
        "🤖 AI: Неон (меню)")
            bash "$HOME/rumix/scripts/neon-menu.sh"
            ;;
        "🤖 Agent Runtime")
            bash "$HOME/rumix/scripts/agents-menu.sh"
            ;;
        "🦊 AI: Фурия (меню)")
            bash "$HOME/rumix/scripts/fury-menu.sh"
            ;;
        "📦 Установить Неона")
            bash "$HOME/rumix/scripts/install-neon.sh"
            read -p "Enter..."
            ;;
        "🌿 Git: Work")
            cd ~/Work && git status
            exec zsh
            ;;
        "🌊 Rumix Shell")
            bash "$HOME/rumix/scripts/shell-start.sh"
            read -p "Enter..."
            ;;
        "📁 Проекты")
            bash "$HOME/rumix/scripts/projects-menu.sh"
            ;;
        "🗂  Файлы")
            bash "$HOME/rumix/scripts/files-menu.sh"
            ;;
        "🐙 GitHub")
            bash "$HOME/rumix/scripts/github-menu.sh"
            ;;
        "⚙️  Настройки и память")
            bash "$HOME/rumix/scripts/settings-menu.sh"
            ;;
        "📖 Инструкция")
            clear
            less "$HOME/Work/blocks/cards/rumix-first-time.md"
            ;;
        "🚪 Выход")
            echo "🧬 До встречи, Мыслитель."
            exit 0
            ;;
    esac
    done
