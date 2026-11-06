#!/data/data/com.termux/files/usr/bin/bash
cd "$HOME/rumix-ecosystem" || exit 1
while true; do
    clear
    echo "================================================="
    echo "           🧬 RUMIX — НЕОНОВЫЙ ШЁПОТ           "
    echo "================================================="
    STORAGE=$(df -h ~ 2>/dev/null | awk 'NR==2 {print $4}')
    RAM=$(free -m 2>/dev/null | awk 'NR==2 {print $7}')
    echo "  💾 ${STORAGE:-?}   🧠 ${RAM:-?} MB   🌐 Online"
    echo ""
    PS3="👉 Введи номер действия: "
    options=("🌊 Оболочка (запуск всего)" "🔄 Синхронизация" "🛡️ Фурия (аудит)" "🗺️ Карта дома" "📁 Проекты" "🛠️ Prompt Forge" "💬 Чат с Неоном" "🔐 GitHub" "🚪 Выход")
    select choice in "${options[@]}"; do
        case $choice in
            "🌊 Оболочка (запуск всего)") bash scripts/launch-all.sh; read -p "Enter..." ;;
            "🔄 Синхронизация") bash scripts/sync-all.sh; read -p "Enter..." ;;
            "🛡️ Фурия (аудит)") bash scripts/fury-light.sh; read -p "Enter..." ;;
            "🗺️ Карта дома") cat RUMIX_MAP.md | less; read -p "Enter..." ;;
            "📁 Проекты") bash scripts/projects-menu.sh; read -p "Enter..." ;;
            "🛠️ Prompt Forge") bash scripts/forge-manager.sh start; bash scripts/forge-manager.sh status; read -p "Enter..." ;;
            "💬 Чат с Неоном") bash scripts/neon-chat.sh; read -p "Enter..." ;;
            "🔐 GitHub") bash scripts/github-auth.sh; read -p "Enter..." ;;
            "🚪 Выход") echo "До встречи, Зая!"; exit 0 ;;
            *) echo "⚠️ Неверный выбор." ;;
        esac
    done
done
