"""services.py — управление процессами дома из Shell."""
import subprocess
from pathlib import Path
from core.modules import module, ModuleResult

m = module("services", "Сервисы", "⚙️", "Управление Shell, Неоном и Scanner.")

SVC_SCRIPT = Path.home() / 'rumix-ecosystem' / 'scripts' / 'svc-manager.sh'

def _run(cmd):
    try:
        r = subprocess.run(['bash', str(SVC_SCRIPT)] + cmd, capture_output=True, text=True, timeout=15)
        return r.stdout.strip() + ("\n" + r.stderr.strip() if r.stderr else "")
    except Exception as e:
        return f"Ошибка: {e}"

@m.get
def state():
    """Статус всех сервисов."""
    out = _run(['status'])
    return ModuleResult({"status_report": out})

@m.post
def action(data):
    """POST {"action": "start|stop", "svc": "shell|neon|scanner|all"}"""
    act = data.get("action")
    svc = data.get("svc", "all")
    
    if act not in ("start", "stop"):
        return ModuleResult({"error": "action должен быть 'start' или 'stop'"}, code=400)
    if svc not in ("shell", "neon", "scanner", "all"):
        return ModuleResult({"error": "svc должен быть 'shell', 'neon', 'scanner' или 'all'"}, code=400)
        
    out = _run([act, svc])
    return ModuleResult({"result": out})
