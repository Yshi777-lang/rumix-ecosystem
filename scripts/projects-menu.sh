#!/data/data/com.termux/files/usr/bin/bash
# projects-menu.sh — проекты дома 📁

# Список проектов: имя|путь|описание
PROJECTS=(
    "🌿 Work (душа дома)|$HOME/Work|Ядро, летопись, карты"
    "🧬 Rumix (тело дома)|$HOME/rumix|Терминал, скрипты, Agent Runtime"
    "🧪 Tiamat-ai- (лаборатория)|$HOME/Tiamat-ai-|Эксперименты, NobodyWho, APK"
    "🤖 Deepseek-API|$HOME/Deepseek-API|API эксперимент (отложен)"
    "📦 models|$HOME/models|Локальные LLM (Qwen 0.6B, 1.5B)"
    "💾 Download|$HOME/storage/shared/Download|Загрузки, бекапы"
    "🔙 Назад в Rumix|_back_|"
)

while true; do
    clear
    gum style --border normal --padding "0 2" --border-foreground 33 "📁 ПРОЕКТЫ ДОМА"

    # Список имён
    NAMES=()
    for p in "${PROJECTS[@]}"; do
        NAMES+=("$(echo "$p" | cut -d'|' -f1)")
    done

    choice=$(printf '%s\n' "${NAMES[@]}" | gum choose --height 10)

    case "$choice" in
        "🔙 Назад в Rumix")
            exit 0
            ;;
        *)
            # Найти выбранный проект
            for p in "${PROJECTS[@]}"; do
                name=$(echo "$p" | cut -d'|' -f1)
                path=$(echo "$p" | cut -d'|' -f2)
                desc=$(echo "$p" | cut -d'|' -f3)
                if [ "$name" = "$choice" ]; then
                    clear
                    echo "📁 $name"
                    echo "   Путь: $path"
                    echo "   $desc"
                    echo ""

                    if [ ! -d "$path" ]; then
                        echo "⚠️  Папка не существует: $path"
                        read -p "Enter..."
                        break
                    fi

                    # Меню проекта
                    action=$(gum choose \
                        "📂 Открыть в zsh" \
                        "📋 Показать содержимое" \
                        "🔀 Git status" \
                        "🔙 К списку проектов")

                    case "$action" in
                        "📂 Открыть в zsh")
                            cd "$path" && exec zsh
                            ;;
                        "📋 Показать содержимое")
                            clear
                            ls -la "$path"
                            echo ""
                            read -p "Enter..."
                            ;;
                        "🔀 Git status")
                            clear
                            if [ -d "$path/.git" ]; then
                                cd "$path" && git status -s && git branch --show-current
                            else
                                echo "⚠️  Не git-репозиторий"
                            fi
                            echo ""
                            read -p "Enter..."
                            ;;
                        "🔙 К списку проектов")
                            break
                            ;;
                    esac
                    break
                fi
            done
            ;;
    esac
done
