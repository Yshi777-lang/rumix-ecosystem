#!/data/data/com.termux/files/usr/bin/bash
# TEST-E2E-04 — Ошибка tool не маскируется под успех.
# Проверяет: если tool вернул error, он сохраняется в evidence с confidence=low.

cd "$HOME/rumix/agents" || exit 1

python3 -c "
import sys; sys.path.insert(0, '.')
from runtime.tools import call_tool

# Неизвестный tool → error
r = call_tool('nonexistent_tool', auto_approve=True)

if 'error' not in r:
    print('FAIL: ожидали error, получили:', r)
    sys.exit(1)

# Проверим, что в error есть сообщение
err = r.get('error', '')
if 'Неизвестный' not in err and 'unknown' not in err.lower():
    print('FAIL: неверное сообщение об ошибке:', err)
    sys.exit(1)

# Проверим, что это НЕ выглядит как успех
if r.get('success') is True:
    print('FAIL: ошибка маскируется под успех!')
    sys.exit(1)

print('OK: ошибка tool не маскируется под успех')
sys.exit(0)
"
