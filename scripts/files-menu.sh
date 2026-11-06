#!/data/data/com.termux/files/usr/bin/bash
# files-menu.sh — просмотр и редактор файлов (Pure Bash Edition)
CURRENT_DIR="$HOME"
icon_for() {
    case "${1##*.}" in
        sh|bash|zsh) echo "🔧" ;; py) echo "🐍" ;; json|jsonl) echo "📋" ;;
        md|txt) echo "📝" ;; tar|gz|zip) echo "📦" ;; js|ts) echo "⚙️" ;; *) echo "📄" ;;
    esac
}
browse_dir() {
    while true; do
        clear
        echo "================================================="
        echo "           📁 ФАЙЛОВЫЙ МЕНЕДЖЕР: $CURRENT_DIR           "
        echo "================================================="
        PS3="👉 Введи номер действия: "
        local options=("⬆  ..")
        while IFS= read -r d; do
            [ -z "$d" ] && continue
            options+=("📂 $(basename "$d")")
        done < <(find "$CURRENT_DIR" -maxdepth 1 -mindepth 1 -type d 2>/dev/null | sort | head -50)
        while IFS= read -r f; do
            [ -z "$f" ] && continue
            local size=$(du -h "$f" 2>/dev/null | cut -f1)
            local icon=$(icon_for "$f")
            options+=("$icon $(basename "$f") ($size)")
        done < <(find "$CURRENT_DIR" -maxdepth 1 -mindepth 1 -type f 2>/dev/null | sort | head -50)
        options+=("⬅  Назад в Rumix" "🚪 Выход")
        
        select choice in "${options[@]}"; do
            if [[ "$choice" == "⬆  .." ]]; then CURRENT_DIR=$(dirname "$CURRENT_DIR"); break
            elif [[ "$choice" == "⬅  Назад в Rumix" || -z "$choice" ]]; then return 0
            elif [[ "$choice" == "🚪 Выход" ]]; then echo "📁 До встречи."; exit 0
            elif [[ "$choice" == 📂\ * ]]; then CURRENT_DIR="$CURRENT_DIR/${choice#📂 }"; break
            elif [[ -n "$choice" ]]; then
                local fname=$(echo "$choice" | sed -E 's/^[^ ]+ //; s/  \([^)]+\)$//')
                handle_file "$CURRENT_DIR/$fname"; break
            else echo "⚠️ Неверный выбор."; fi
        done
    done
}
handle_file() {
    local file="$1"
    [ ! -f "$file" ] && { echo "⚠️ Файл не найден"; sleep 1; return; }
    echo "Файл: $file"
    PS3="👉 Выбери действие: "
    select action in "👁 Открыть (первые 50 строк)" "✏️ Редактировать (nano)" "📋 Копировать в Downloads" "🗑 Удалить" "⬅ Назад"; do
        case "$action" in
            "👁 Открыть (первые 50 строк)") head -50 "$file"; read -r -p "Enter..."; break ;;
            "✏️ Редактировать (nano)") nano "$file"; break ;;
            "📋 Копировать в Downloads")
                local dest="$HOME/storage/shared/Download/$(basename "$file")"
                cp "$file" "$dest" && echo "✅ Скопировано" || echo "❌ Ошибка"; sleep 1; break ;;
            "🗑 Удалить")
                read -r -p "Удалить $(basename "$file")? (y/N): " confirm
                if [[ "$confirm" == [Yy]* ]]; then rm -f "$file" && echo "✅ Удалено" || echo "❌ Ошибка"; fi
                sleep 1; break ;;
            "⬅ Назад"|"") break ;;
            *) echo "⚠️ Неверный выбор." ;;
        esac
    done
}
browse_dir
