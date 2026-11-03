#!/data/data/com.termux/files/usr/bin/bash
# TEST-E2E-03 — Недоступная capability → структурный отказ.
# Проверяет: call_tool блокирует tool, если capability недоступна.

cd "$HOME/rumix/agents" || exit 1

python3 -c "
import sys; sys.path.insert(0, '.')
from runtime.tools import call_tool, TOOL_REGISTRY

# network_status имеет allow_partial=True (Победа 63).
# Временно выключим allow_partial + переключим на netlink (UNAVAILABLE).
tool = TOOL_REGISTRY['network_status']
orig_caps = tool.required_capabilities
orig_partial = tool.allow_partial
tool.required_capabilities = ['netlink']
tool.allow_partial = False

try:
    r = call_tool('network_status', auto_approve=True)
finally:
    tool.required_capabilities = orig_caps
    tool.allow_partial = orig_partial

# Ожидаем: structured отказ
if 'error' not in r:
    print('FAIL: ожидали error, получили:', r)
    sys.exit(1)

if r.get('error') != 'capability_unavailable':
    print('FAIL: ожидали capability_unavailable, получили:', r.get('error'))
    sys.exit(1)

if r.get('capability') != 'netlink':
    print('FAIL: ожидали capability=netlink, получили:', r.get('capability'))
    sys.exit(1)

if not r.get('reason'):
    print('FAIL: нет поля reason в отказе')
    sys.exit(1)

# Проверим, что tool НЕ запустился (нет поля data)
if 'data' in r:
    print('FAIL: tool запустился, несмотря на недоступную capability')
    sys.exit(1)

print('OK: недоступная capability → структурный отказ')
sys.exit(0)
"
