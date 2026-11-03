#!/data/data/com.termux/files/usr/bin/bash
# TEST-E2E-02 — Отказ в разрешении не запускает tool.

cd "$HOME/rumix/agents" || exit 1

python3 -c "
import sys; sys.path.insert(0, '.')
from runtime.tools import call_tool

# run_command требует EXEC. Не даём auto_approve.
# Ожидаем отказ ДО выполнения.
r = call_tool('run_command', auto_approve=False, command='rm -rf /system')

if 'error' not in r:
    print('FAIL: ожидали error (permission denied), получили:', r)
    sys.exit(1)

err = r.get('error', '')
if 'Permission' not in err and 'permission' not in err.lower():
    print('FAIL: ожидали Permission denied, получили:', r)
    sys.exit(1)

# Главное: если в ошибке есть stdout — значит tool запустился.
# Проверим, что результата выполнения нет.
if 'stdout' in r:
    print('FAIL: tool запустился, несмотря на отказ!')
    sys.exit(1)

print('OK: отказ в разрешении не запускает tool')
sys.exit(0)
"
