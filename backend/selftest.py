# selftest.py — самопроверка дома
# Создано: 17.10.2026 (Тиамат + Зая)

import subprocess
import os

def check_permission_gate():
    try:
        from core.bridge.master_gate import master_check
        res = master_check('command', 'ls')
        return {"name": "Permission Gate", "status": "OK", "details": f"Уровень: {res['level']}"}
    except Exception as e:
        return {"name": "Permission Gate", "status": "ERROR", "details": str(e)}

def check_terminal_api():
    try:
        from web.terminal_api import run_command
        res = run_command('echo test')
        if res.get('status') == 'OK':
            return {"name": "Terminal API", "status": "OK", "details": "Отвечает."}
        else:
            return {"name": "Terminal API", "status": "WARN", "details": "Не отвечает."}
    except Exception as e:
        return {"name": "Terminal API", "status": "ERROR", "details": str(e)}

def check_git_api():
    try:
        from backend.git_manager import get_status
        res = get_status()
        if res.get('status') == 'OK':
            return {"name": "Git Rollback", "status": "OK", "details": "Готов к откату."}
        else:
            return {"name": "Git Rollback", "status": "WARN", "details": "Проблема с git."}
    except Exception as e:
        return {"name": "Git Rollback", "status": "ERROR", "details": str(e)}

def run_all():
    """Запускает все проверки."""
    results = []
    results.append(check_permission_gate())
    results.append(check_terminal_api())
    results.append(check_git_api())
    
    # Общий статус
    all_ok = all(r['status'] == 'OK' for r in results)
    return {"overall": "OK" if all_ok else "WARN", "checks": results}
