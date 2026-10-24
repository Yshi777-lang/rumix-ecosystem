#!/data/data/com.termux/files/usr/bin/bash
# loop-submit.sh — добавить задачу в очередь Loop
# Использование:
#   loop-submit.sh <name> < script.sh
#   echo "echo hello" | loop-submit.sh hello
#   loop-submit.sh hello <<< 'echo "test"'

set -e

LOOP_DIR="$HOME/rumix/loop"
OUT_DIR="$LOOP_DIR/out"
QUEUE="$LOOP_DIR/queue.txt"

mkdir -p "$OUT_DIR"
touch "$QUEUE"

name="${1:-}"
if [ -z "$name" ]; then
    echo "❌ Использование: loop-submit.sh <name> [script]"
    echo "   Или: echo 'script' | loop-submit.sh <name>"
    exit 1
fi

# Проверка имени: только [a-zA-Z0-9_-]
if ! echo "$name" | grep -qE '^[a-zA-Z0-9_-]+$'; then
    echo "❌ Имя должно содержать только [a-zA-Z0-9_-]"
    exit 1
fi

script_file="$OUT_DIR/${name}.sh"

# Скрипт: из stdin или из второго аргумента
if [ -n "${2:-}" ]; then
    echo "$2" > "$script_file"
elif [ ! -t 0 ]; then
    cat > "$script_file"
else
    echo "❌ Нет содержимого скрипта"
    exit 1
fi

chmod +x "$script_file"
echo "$name" >> "$QUEUE"

# Метрики
count=$(wc -l < "$QUEUE" 2>/dev/null || echo 0)
echo "✅ $name → out/$name.sh"
echo "📋 Очередь: $count задач"
