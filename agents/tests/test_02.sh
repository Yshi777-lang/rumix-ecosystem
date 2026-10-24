#!/data/data/com.termux/files/usr/bin/bash
# test_02 — system_info: required_capabilities=[] -> OK

cd "$HOME/rumix/agents" || exit 1

python3 -c "
import sys; sys.path.insert(0, '.')
from runtime.tools import call_tool

r = call_tool('system_info', auto_approve=True)
if 'error' in r:
    print('FAIL: unexpected error:', r)
    sys.exit(1)
print('OK: system_info выполнен')
sys.exit(0)
"
