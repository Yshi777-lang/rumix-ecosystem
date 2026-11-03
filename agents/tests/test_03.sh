#!/data/data/com.termux/files/usr/bin/bash
# test_03 — system_info + netlink -> capability_unavailable

cd "$HOME/rumix/agents" || exit 1

python3 -c "
import sys; sys.path.insert(0, '.')
from runtime.tools import TOOL_REGISTRY, call_tool

# Временно добавим netlink
TOOL_REGISTRY['system_info'].required_capabilities = ['netlink']

r = call_tool('system_info', auto_approve=True)

# Восстановим
TOOL_REGISTRY['system_info'].required_capabilities = []

if r.get('error') != 'capability_unavailable':
    print('FAIL: ожидали capability_unavailable, получили:', r)
    sys.exit(1)
if r.get('capability') != 'netlink':
    print('FAIL: ожидали capability=netlink, получили:', r)
    sys.exit(1)
print('OK: capability_unavailable корректен')
sys.exit(0)
"
