#!/data/data/com.termux/files/usr/bin/bash
# Неон — редактор характера
# Неоновый шёпот. 🤖

FILE="$HOME/rumix/neon/character.md"

if [ ! -f "$FILE" ]; then
    echo "⚠️  Файл характера не найден."
    exit 1
fi

while true; do
    echo ""
    gum style --border normal --padding "0 1" "🤖 ХАРАКТЕР НЕОНА"
    echo ""
    echo "Текущий характер:"
    echo "──────────────"
    cat -n "$FILE"
    echo "──────────────"
    echo ""

    choice=$(gum choose "Добавить фразу" "Удалить строку" "Править строку" "Очистить" "Выход")

    case "$choice" in
        "Добавить фразу")
            NEW=$(gum input --placeholder "Новая фраза для характера")
            [ -n "$NEW" ] && echo "$NEW" >> "$FILE" && echo "✅ Добавлено"
            ;;
        "Удалить строку")
            LINE=$(gum input --placeholder "Номер строки для удаления")
            if [ -n "$LINE" ] && [ "$LINE" -gt 0 ] 2>/dev/null; then
                sed -i "${LINE}d" "$FILE"
                echo "✅ Строка $LINE удалена"
            else
                echo "⚠️  Неверный номер"
            fi
            ;;
        "Править строку")
            LINE=$(gum input --placeholder "Номер строки для правки")
            if [ -n "$LINE" ] && [ "$LINE" -gt 0 ] 2>/dev/null; then
                OLD=$(sed -n "${LINE}p" "$FILE")
                NEW=$(gum input --value "$OLD" --placeholder "Новый текст")
                if [ -n "$NEW" ]; then
                    sed -i "${LINE}s|.*|$NEW|" "$FILE"
                    echo "✅ Строка $LINE обновлена"
                fi
            else
                echo "⚠️  Неверный номер"
            fi
            ;;
        "Очистить")
            if gum confirm "Очистить весь характер?"; then
                > "$FILE"
                echo "✅ Очищено"
            fi
            ;;
        "Выход")
            echo "🤖 До встречи, Зая."
            exit 0
            ;;
    esac
done
