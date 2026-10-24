# git_manager.py — управление git через API
# Создано: 17.10.2026 (Тиамат + Зая)
# Обновлено: 17.10 (полный откат: checkout + clean)

import subprocess
import os

REPO_PATH = os.path.expanduser("~/rumix")

def get_status():
    """Показывает, что изменилось."""
    try:
        result = subprocess.run(
            ["git", "-C", REPO_PATH, "status", "--short"],
            capture_output=True, text=True, timeout=10
        )
        return {"status": "OK", "output": result.stdout.strip() or "Чисто."}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

def rollback():
    """Откатывает ВСЕ незакоммиченные изменения (включая новые файлы)."""
    try:
        # 1. Откат изменённых файлов
        subprocess.run(
            ["git", "-C", REPO_PATH, "checkout", "."],
            capture_output=True, text=True, timeout=10
        )
        # 2. Удаление новых (неотслеживаемых) файлов
        result = subprocess.run(
            ["git", "-C", REPO_PATH, "clean", "-fd"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return {"status": "OK", "message": "Все изменения и новые файлы откачены."}
        else:
            return {"status": "ERROR", "message": result.stderr.strip()}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}
