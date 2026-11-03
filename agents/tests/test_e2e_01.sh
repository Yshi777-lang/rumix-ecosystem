#!/data/data/com.termux/files/usr/bin/bash
# TEST-E2E-01 — Корректный сценарий проходит end-to-end.
# Цепочка: Intent → Schema → Capability → Permission → Tool → Evidence → Validation → Result → Verification.

cd "$HOME/rumix/agents" || exit 1

python3 -c "
import sys; sys.path.insert(0, '.')
from runtime.tools import call_tool, TOOL_REGISTRY

# Берём system_info — простой tool без capability
tool = TOOL_REGISTRY.get('system_info')
if not tool:
    print('FAIL: system_info не найден')
    sys.exit(1)

# Шаг 1: Schema — есть
if not hasattr(tool, 'input_schema'):
    print('FAIL: нет input_schema')
    sys.exit(1)

# Шаг 2: Capability — пусто (required_capabilities = [])
if tool.required_capabilities:
    print('FAIL: system_info должен иметь пустые required_capabilities')
    sys.exit(1)

# Шаг 3: Permission — READ
from runtime.permissions import Permission
if Permission.READ not in tool.permissions:
    print('FAIL: system_info должен требовать READ')
    sys.exit(1)

# Шаг 4: Tool — выполняется
r = call_tool('system_info', auto_approve=True)
if 'error' in r:
    print('FAIL: system_info вернул error:', r)
    sys.exit(1)

# Шаг 5: Evidence — есть данные
if not r:
    print('FAIL: пустой результат')
    sys.exit(1)

print('OK: end-to-end прошёл (Intent → Tool → Evidence → Result)')
sys.exit(0)
"
