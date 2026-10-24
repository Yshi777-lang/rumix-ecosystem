# ~/rumix/web/terminal_api.py
# API для веб-терминала. Пока — базовая версия.
# Создано: 17.10.2026 (Тиамат + Зая)

import sys
sys.path.insert(0, '/data/data/com.termux/files/home/rumix')
from core.bridge.master_gate import master_check

def run_command(cmd: str, user_consent: bool = False) -> dict:
    """
    Проверяет и выполняет команду для веб-терминала.
    """
    check = master_check('command', cmd)
    
    if not check['allowed'] and not user_consent:
        return {
            'status': 'DENIED',
            'level': check['level'],
            'message': check['message'],
            'output': None
        }
        
    if check['level'] == 'BLOCKED':
        return {
            'status': 'BLOCKED',
            'level': 'BLOCKED',
            'message': check['message'],
            'output': None
        }

    try:
        from core.bridge.safe_bridge import execute_safe
        res = execute_safe('command', cmd, user_consent=user_consent)
        return res
    except Exception as e:
        return {'status': 'ERROR', 'message': str(e), 'output': None}
