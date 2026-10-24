#!/data/data/com.termux/files/usr/bin/bash
# files-menu.sh — просмотр и редактор файлов
# Rumix. 📁

CURRENT_DIR="$HOME"

# Иконка по расширению
icon_for() {
    local f="$1"
    case "${f##*.}" in
        sh|bash|zsh) echo "🔧" ;;
        py)          echo "🐍" ;;
        json|jsonl)  echo "📋" ;;
        md|txt)      echo "📝" ;;
        tar|gz|zip)  echo "📦" ;;
        jsonl.gz)    echo "📦" ;;
        js|ts)       echo "⚙️" ;;
        png|jpg|jpeg) echo "🖼" ;;
        *)           echo "📄" ;;
    esac
}

# Показать список файлов + действий
browse_dir() {
    while true; do
        clear
        gum style --border normal --padding "0 2" --border-foreground 93 "📁 $CURRENT_DIR"

        # Собираем список
        local items=()
        items+=("⬆  ..")

        # Сначала папки
        while IFS= read -r d; do
            [ -z "$d" ] && continue
            items+=("📂 $(basename "$d")")
        done < <(find "$CURRENT_DIR" -maxdepth 1 -mindepth 1 -type d 2>/dev/null | sort | head -50)

        # Потом файлы
        while IFS= read -r f; do
            [ -z "$f" ] && continue
            local size icon
            size=$(du -h "$f" 2>/dev/null | cut -f1)
            icon=$(icon_for "$f")
            items+=("$icon $(basename "$f")  ($size)")
        done < <(find "$CURRENT_DIR" -maxdepth 1 -mindepth 1 -type f 2>/dev/null | sort | head -50)

        items+=("⬅  Назад в Rumix")
        items+=("🚪 Выход")

        local choice
        choice=$(gum choose "${items[@]}")

        case "$choice" in
            "⬆  ..")
                CURRENT_DIR=$(dirname "$CURRENT_DIR")
                ;;
            "⬅  Назад в Rumix"|"")
                exit 0
                ;;
            "🚪 Выход")
                echo "📁 До встречи."
                exit 0
                ;;
            "📂 "*)
                local name="${choice#📂 }"
                CURRENT_DIR="$CURRENT_DIR/$name"
                ;;
            *)
                # Файл — отделяем имя от размера
                local fname
                fname=$(echo "$choice" | sed -E 's/^[^ ]+ //; s/  \([^)]+\)$//')
                handle_file "$CURRENT_DIR/$fname"
                ;;
        esac
    done
}

# Действия с файлом
handle_file() {
    local file="$1"
    [ ! -f "$file" ] && { echo "⚠️  Файл не найден"; sleep 1; return; }

    local action
    action=$(gum choose \
        "👁  Открыть (cat, первые 50 строк)" \
        "✏️  Редактировать (nano)" \
        "📋  Копировать в Downloads" \
        "🗑  Удалить" \
        "⬅  Назад")

    case "$action" in
        "👁  Открыть (cat, первые 50 строк)")
            head -50 "$file"
            echo ""
            read -r -p "Enter для продолжения..."
            ;;
        "✏️  Редактировать (nano)")
            nano "$file"
            ;;
        "📋  Копировать в Downloads")
            local dest="$HOME/storage/shared/Download/$(basename "$file")"
            cp "$file" "$dest" && echo "✅ Скопировано: $dest" || echo "❌ Ошибка"
            sleep 1
            ;;
        "🗑  Удалить")
            if gum confirm "Удалить $(basename "$file")?"; then
                rm -f "$file" && echo "✅ Удалено" || echo "❌ Ошибка"
                sleep 1
            fi
            ;;
    esac
}

browse_dir
