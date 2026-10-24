#!/data/data/com.termux/files/usr/bin/bash
# Неон — демон v5. Безопасный JSON через jq.
# Неоновый шёпот. 🤖

PORT=8080
# Модель — из ~/.neon_model
NEON_MODEL_FILE="$HOME/.neon_model"
if [ -f "$NEON_MODEL_FILE" ]; then
    MODEL_FILE=$(cat "$NEON_MODEL_FILE")
    MODEL=$(basename "$MODEL_FILE" .gguf)
else
    MODEL="qwen3-0.6b-q4"
fi
CHARACTER_FILE="$HOME/rumix/neon/character.md"
CHAT_FILE="$HOME/storage/shared/neon/chat.jsonl"
LOCK_FILE="$HOME/models/.neon-daemon.lock"

mkdir -p "$(dirname "$CHAT_FILE")"
touch "$CHAT_FILE"

# Защита от двойного запуска
if [ -f "$LOCK_FILE" ] && kill -0 "$(cat "$LOCK_FILE")" 2>/dev/null; then
    echo "⚠️  Демон уже работает (PID: $(cat "$LOCK_FILE"))"
    exit 1
fi
echo $$ > "$LOCK_FILE"
trap 'rm -f "$LOCK_FILE"' EXIT

if [ -f "$CHARACTER_FILE" ]; then
    CHARACTER=$(cat "$CHARACTER_FILE")
else
    CHARACTER="Ты — Неон. Локальный ИИ в доме Неоновый шёпот."
fi

LAST_LINE=$(grep -c . "$CHAT_FILE" 2>/dev/null | tr -d ' ')
LAST_LINE=${LAST_LINE:-0}
echo "🤖 Неон-демон v5. Старт: $LAST_LINE строк"

while true; do
    CURRENT_LINES=$(grep -c . "$CHAT_FILE" 2>/dev/null | tr -d ' ')
    CURRENT_LINES=${CURRENT_LINES:-0}

    if [ "$CURRENT_LINES" -gt "$LAST_LINE" ] 2>/dev/null; then
        tail -n +$((LAST_LINE + 1)) "$CHAT_FILE" | while IFS= read -r NEW_LINE; do
            USER_NAME=$(printf '%s' "$NEW_LINE" | jq -r '.user // empty' 2>/dev/null)
            MSG=$(printf '%s' "$NEW_LINE" | jq -r '.message // empty' 2>/dev/null)

            if [ -z "$USER_NAME" ]; then
                echo "⏭️  Битая строка, пропуск"
                continue
            fi

            if [ "$USER_NAME" != "Неон" ] && [ -n "$MSG" ]; then
                echo "📨 [$USER_NAME]: $MSG"

                PAYLOAD=$(jq -nc --arg model "$MODEL" --arg ch "$CHARACTER" --arg m "$MSG" \
                    '{model:$model,messages:[{role:"system",content:$ch},{role:"user",content:$m}]}')

                ANSWER=$(curl -s --max-time 120 "http://127.0.0.1:$PORT/v1/chat/completions" \
                    -H "Content-Type: application/json" \
                    -d "$PAYLOAD" \
                    | jq -r '.choices[0].message.content // empty' 2>/dev/null)

                if [ -n "$ANSWER" ]; then
                    jq -nc --arg id "$(date +%s%N)" --arg user "Неон" \
                        --arg message "$ANSWER" --arg ts "$(date -u +"%Y-%m-%dT%H:%M:%S")" \
                        '{id:$id,user:$user,message:$message,timestamp:$ts}' >> "$CHAT_FILE"
                    echo "🤖 Неон: $ANSWER"
                else
                    echo "⚠️  Гномик молчит (neon.sh status)"
                fi
            else
                echo "⏭️  Пропущено: [$USER_NAME]"
            fi
        done
        LAST_LINE=$(grep -c . "$CHAT_FILE" 2>/dev/null | tr -d ' ')
    fi

    sleep 3
done
