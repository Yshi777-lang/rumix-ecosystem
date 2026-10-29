#!/data/data/com.termux/files/usr/bin/bash
# loop-gate.sh — проверка задач Loop через Master Gate.
# Обновлено: 28.10.2026 — безопасная передача через stdin.

FILE="$1"
if [ ! -f "$FILE" ]; then
    echo "❌ Loop Gate: файл не найден: $FILE"
    exit 1
fi

# Передаём содержимое через stdin в Python, без вставки в код
RESULT=$(python3 -c "
import sys
sys.path.insert(0, '$HOME/rumix')
from core.bridge.master_gate import master_check
content = sys.stdin.read()
try:
    res = master_check('command', content)
    allowed = str(res['allowed'])
    level = str(res['level'])
    msg = str(res['message']).replace('\n', ' ')
    print(f'{allowed}|{level}|{msg}')
except Exception as e:
    print(f'False|ERROR|Ошибка гейта: {e}')
" < "$FILE" 2>&1)

ALLOWED=$(echo "$RESULT" | cut -d'|' -f1)
LEVEL=$(echo "$RESULT" | cut -d'|' -f2)
MESSAGE=$(echo "$RESULT" | cut -d'|' -f3)

if [ "$ALLOWED" = "True" ]; then
    echo "✅ Loop Gate: разрешено ($LEVEL)."
    exit 0
else
    echo "❌ Loop Gate: отклонено ($LEVEL). $MESSAGE"
    exit 1
fi
