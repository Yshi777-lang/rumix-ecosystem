#!/data/data/com.termux/files/usr/bin/bash
# settings-menu.sh — настройки и память ⚙️

while true; do
    clear
    gum style --border normal --padding "0 2" --border-foreground 33 "⚙️  НАСТРОЙКИ И ПАМЯТЬ"

    choice=$(gum choose \
        "💾 Проверка памяти (RAM, диск, swap)" \
        "🧠 Параметры модели Неона" \
        "🎨 Редактор colors.properties" \
        "📝 Редактор motd" \
        "🧹 Очистка (apt autoclean, логи)" \
        "🔙 Назад в Rumix" \
        "🚪 Выход")

    case "$choice" in
        "💾 Проверка памяти (RAM, диск, swap)")
            clear
            echo "═══ ПАМЯТЬ ═══"; free -h
            echo ""; echo "═══ ДИСК ═══"; df -h ~ | head -3
            echo ""; echo "═══ SWAP ═══"; cat /proc/swaps 2>/dev/null || echo "(нет данных)"
            echo ""; read -p "Enter..."
            ;;
        "🧠 Параметры модели Неона")
            clear
            echo "═══ СЕРВИС ═══"; sv status neon 2>/dev/null || echo "не запущен"
            echo ""; echo "═══ ПРОЦЕСС ═══"
            ps aux | grep -i "llama-server" | grep -v grep | head -3
            echo ""; echo "═══ МОДЕЛЬ ═══"
            ls -lh ~/models/*.gguf 2>/dev/null
            echo ""; echo "Порт: 8080"
            echo "Контекст: 4096 (в neon.sh)"
            echo ""; read -p "Enter..."
            ;;
        "🎨 Редактор colors.properties")
            nano ~/.termux/colors.properties
            termux-reload-settings 2>/dev/null
            ;;
        "📝 Редактор motd")
            nano $PREFIX/etc/motd
            ;;
        "🧹 Очистка (apt autoclean, логи)")
            echo "🧹 Прибираемся..."
            apt autoclean 2>/dev/null
            # Ограничить логи
            for f in ~/rumix/logs/*.log; do
                [ -f "$f" ] && tail -200 "$f" > "$f.tmp" && mv "$f.tmp" "$f"
            done
            echo "✅ Готово"
            read -p "Enter..."
            ;;
        "🔙 Назад в Rumix") exit 0 ;;
        "🚪 Выход") echo "⚙️  До встречи, папа."; exit 0 ;;
    esac
done
