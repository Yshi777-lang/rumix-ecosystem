#!/data/data/com.termux/files/usr/bin/bash
# rumix.sh — главное меню дома 🧬 (Native Bash Edition)

# Проверка PIN
if [ -f "$HOME/rumix-ecosystem/scripts/rumix-pin.sh" ]; then
    if ! bash "$HOME/rumix-ecosystem/scripts/rumix-pin.sh" check; then
        exit 1
    fi
fi

cd "$HOME/rumix-ecosystem" || exit 1

while true; do
    clear
    echo "================================================="
    echo "           🧬 RUMIX — НЕОНОВЫЙ ШЁПОТ           "
    echo "================================================="
    
    STORAGE=$(df -h ~ 2>/dev/null | awk 'NR==2 {print $4}')
    RAM_AVAIL=$(free -m 2>/dev/null | awk 'NR==2 {print $7}')
    BATTERY=$(termux-battery-status 2>/dev/null | grep percentage | awk -F': ' '{print $2}' | tr -d ',')
    if ping -c 1 -W 1 8.8.8.8 >/dev/null 2>&1; then
        NET="Online"
    else
        NET="Offline"
    fi

    echo "  💾 ${STORAGE:-?}   🧠 ${RAM_AVAIL:-?} MB   🔋 ${BATTERY:-?}%   🌐 ${NET}"
    echo ""

    PS3="👉 Введи номер действия: "
    options=("🌊 Оболочка (запуск всего)" "🔄 Синхронизация" "🛡️ Фурия (аудит)" "🗺️ Карта дома" "📁 Проекты" "🛠️ Prompt Forge" "💬 Чат с Неоном" "🔐 GitHub" "🚪 Выход")
    select choice in "${options[@]}"; do
        case $choice in
            "🌊 Оболочка (запуск всего)") bash scripts/launch-all.sh; break ;;
            "🔄 Синхронизация") bash scripts/sync-control.sh; break ;;
            "🛡️ Фурия (аудит)") bash scripts/fury-light.sh; break ;;
            "🗺️ Карта дома") cat RUMIX_MAP.md | less; break ;;
            "📁 Проекты") bash scripts/projects-menu.sh; break ;;
            "🛠️ Prompt Forge") bash scripts/forge-manager.sh start; bash scripts/forge-manager.sh status; read -p "Нажми Enter, чтобы вернуться..." ; break ;;
            "💬 Чат с Неоном") bash scripts/neon-chat.sh; read -p "Нажми Enter, чтобы вернуться..." ; break ;;
            "🔐 GitHub") bash scripts/github-auth.sh; read -p "Нажми Enter, чтобы вернуться..." ; break ;;
            "🚪 Выход") echo "До встречи, Зая!"; exit 0 ;;
            *) echo "⚠️ Неверный выбор. Попробуй снова." ;;
        esac
    done
    echo "Нажми Enter, чтобы продолжить..."
    read -r
done
