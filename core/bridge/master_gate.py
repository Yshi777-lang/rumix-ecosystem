# ~/rumix/core/bridge/master_gate.py
# Единые врата дома. Проверяют всё: команды, файлы, действия.
# Создано: 17.10.2026 (Тиамат + Зая)

from .gate import check_action
from .file_gate import check_file

def master_check(action_type: str, payload: str, user_consent: bool = False) -> dict:
    """
    Единая точка входа для всех действий.
    action_type: 'command' | 'file_read' | 'file_write'
    """
    if action_type == 'command':
        return check_action('command', payload)
    
    if action_type == 'file_read':
        return check_file(payload, 'read')
        
    if action_type == 'file_write':
        return check_file(payload, 'write')
        
    return {"allowed": False, "level": "UNKNOWN", "message": "Неизвестный тип действия."}
