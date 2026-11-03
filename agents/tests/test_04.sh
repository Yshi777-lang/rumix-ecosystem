#!/data/data/com.termux/files/usr/bin/bash
# test_04 — network_status + netlink (UNAVAILABLE) + allow_partial → status=partial

cd "$HOME/rumix/agents" || exit 1

python3 -c "
import sys; sys.path.insert(0, '.')
from runtime.tools import TOOL_REGISTRY, call_tool

# Временно netlink
orig = TOOL_REGISTRY['network_status'].required_capabilities
TOOL_REGISTRY['network_status'].required_capabilities = ['netlink']

r = call_tool('network_status', auto_approve=True)

# Восстановим
TOOL_REGISTRY['network_status'].required_capabilities = orig

if 'error' in r:
    print('FAIL: unexpected error:', r)
    sys.exit(1)
if r.get('status') != 'partial':
    print('FAIL: ожидали status=partial, получили:', r.get('status'))
    sys.exit(1)
print('OK: status=partial')
sys.exit(0)
"
