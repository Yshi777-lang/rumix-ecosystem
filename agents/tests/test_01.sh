#!/data/data/com.termux/files/usr/bin/bash
# test_01 — network_status: required_capabilities satisfied -> OK

cd "$HOME/rumix/agents" || exit 1

python3 -c "
import sys; sys.path.insert(0, '.')
from runtime.tools import call_tool

r = call_tool('network_status', auto_approve=True)
if 'error' in r:
    print('FAIL: unexpected error:', r)
    sys.exit(1)
print('OK: network_status выполнен')
sys.exit(0)
"
