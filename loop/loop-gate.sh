#!/data/data/com.termux/files/usr/bin/bash
# loop-gate.sh — проверка задач Loop через Master Gate.
# Создано: 17.10.2026 (Тиамат + Зая)
# Обновлено: 17.10 (фикс зависания)

FILE="$1"
CONTENT=$(cat "$FILE")

# Отправляем на проверку в Python (Master Gate)
RESULT=$(python3 -c "
import sys
sys.path.insert(0, '$HOME/rumix')
from core.bridge.master_gate import master_check
try:
    res = master_check('command', '''$CONTENT''')
    allowed = str(res['allowed'])
    level = str(res['level'])
    msg = str(res['message']).replace('\n', ' ')
    print(f'{allowed}|{level}|{msg}')
except Exception as e:
    print(f'False|ERROR|Ошибка гейта: {e}')
" 2>&1)

# Разбираем результат
ALLOWED=$(echo "$RESULT" | cut -d'|' -f1)
LEVEL=$(echo "$RESULT" | cut -d'|' -f2)
MESSAGE=$(echo "$RESULT" | cut -d'|' -f3)

if [ "$ALLOWED" = "True" ]; then
    echo "✅ Loop Gate: разрешено ($LEVEL)."
    exit 0
else
    echo "🚫 Loop Gate: запрещено ($LEVEL). $MESSAGE"
    exit 1
fi
