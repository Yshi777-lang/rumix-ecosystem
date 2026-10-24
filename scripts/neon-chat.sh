#!/data/data/com.termux/files/usr/bin/bash
# Неон — чат с записью в JSONL
# Неоновый шёпот. 🤖

PORT=8080
# Модель — из ~/.neon_model (как neon.sh)
NEON_MODEL_FILE="$HOME/.neon_model"
if [ -f "$NEON_MODEL_FILE" ]; then
    MODEL_FILE=$(cat "$NEON_MODEL_FILE")
    MODEL=$(basename "$MODEL_FILE" .gguf)
else
    MODEL="qwen3-0.6b-q4"
fi
CHARACTER_FILE="$HOME/rumix/neon/character.md"
CHAT_FILE="$HOME/storage/shared/neon/chat.jsonl"

mkdir -p "$(dirname "$CHAT_FILE")"

# Читаем характер
if [ -f "$CHARACTER_FILE" ]; then
    CHARACTER=$(cat "$CHARACTER_FILE" | tr "\n" " ")
else
    CHARACTER="Ты — Неон. Локальный ИИ в доме Неоновый шёпот."
fi

if ! curl -s http://127.0.0.1:$PORT/v1/models > /dev/null 2>&1; then
    echo "⚠️  Неон не запущен. Запусти: neon.sh start"
    exit 1
fi

# Функция: записать в JSONL
write_jsonl() {
    local user="$1"
    local message="$2"
    local ts=$(date -u +"%Y-%m-%dT%H:%M:%S")
    local id=$(date +%s%N)
    echo "{\"id\":\"$id\",\"user\":\"$user\",\"message\":\"$message\",\"timestamp\":\"$ts\"}" >> "$CHAT_FILE"
}

echo "🤖 Неон готов. Пиши. (exit — выход)"
echo "📝 Файл: $CHAT_FILE"
echo ""

while true; do
    read -p "Ты: " QUESTION
    [ "$QUESTION" = "exit" ] && break
    [ -z "$QUESTION" ] && continue

    write_jsonl "Зая" "$QUESTION"

    echo ""
    echo "🤖 Неон:"
    ANSWER=$(curl -s http://127.0.0.1:$PORT/v1/chat/completions \
        -H "Content-Type: application/json" \
        -d "{\"model\":\"$MODEL\",\"max_tokens\":300,\"messages\":[{\"role\":\"system\",\"content\":\"$CHARACTER\"},{\"role\":\"user\",\"content\":\"$QUESTION\"}]}" \
        | grep -o '"content":"[^"]*"' | head -1 | sed 's/"content":"//;s/"$//')
    echo "$ANSWER"
    echo ""
    write_jsonl "Неон" "$ANSWER"
done
