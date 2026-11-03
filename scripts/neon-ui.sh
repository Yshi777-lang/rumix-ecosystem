#!/data/data/com.termux/files/usr/bin/bash
# Неон — свой UI v2. С автообновлением.
# Неоновый шёпот. 🤖

CHAT_FILE="$HOME/storage/shared/neon/chat.jsonl"

if [ ! -f "$CHAT_FILE" ]; then
    echo "⚠️  Файл чата не найден."
    exit 1
fi

# Показываем сообщение
show_line() {
    local line="$1"
    [ -z "$line" ] && return
    local user=$(echo "$line" | grep -o '"user":"[^"]*"' | cut -d'"' -f4)
    local msg=$(echo "$line" | grep -o '"message":"[^"]*"' | cut -d'"' -f4)

    case "$user" in
        "Неон")  echo "🤖 $user: $msg" ;;
        "Зая")   echo "👤 $user: $msg" ;;
        *)       echo "👥 $user: $msg" ;;
    esac
}

# Заголовок
clear
echo "🤖 Неон — свой UI v2"
echo "📝 Файл: $CHAT_FILE"
echo "════════════════════════════════"
echo ""

# Показываем историю
LAST_LINE=0
while IFS= read -r line; do
    show_line "$line"
    LAST_LINE=$((LAST_LINE + 1))
done < "$CHAT_FILE"

echo ""
echo "════════════════════════════════"

# Автообновление в фоне
(
    while true; do
        CURRENT=$(grep -c . "$CHAT_FILE" 2>/dev/null || echo 0)
        if [ "$CURRENT" -gt "$LAST_LINE" ]; then
            tail -n +$((LAST_LINE + 1)) "$CHAT_FILE" | while IFS= read -r line; do
                show_line "$line"
            done
            LAST_LINE="$CURRENT"
        fi
        sleep 2
    done
) &
UPDATER_PID=$!

# Режим ввода
while true; do
    read -p "Ты: " MSG
    [ "$MSG" = "exit" ] && break
    [ -z "$MSG" ] && continue

    TS=$(date -u +"%Y-%m-%dT%H:%M:%S")
    ID=$(date +%s%N)
    echo "{\"id\":\"$ID\",\"user\":\"Зая\",\"message\":\"$MSG\",\"timestamp\":\"$TS\"}" >> "$CHAT_FILE"
    echo "✅ Отправлено"
done

kill $UPDATER_PID 2>/dev/null
echo "🧬 До встречи, Зая."
