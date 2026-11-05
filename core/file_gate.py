#!/usr/bin/env python3
import os
import subprocess
import sys

# 🛡️ EditorTrue Fusion: Безопасный шлюз файлов
# Этот модуль использует safe-sandbox.sh для изоляции подозрительных операций,
# защищая DATA_HOME от случайного повреждения или выполнения вредоносного кода.

SANDBOX_SCRIPT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts", "safe-sandbox.sh")

def execute_safely(command: str, cwd: str = None) -> dict:
    """
    Выполняет команду в изолированной Zero-Ptrace песочнице.
    Возвращает словарь с 'returncode', 'stdout', 'stderr'.
    """
    if not os.path.exists(SANDBOX_SCRIPT):
        return {"returncode": 1, "stderr": "Safe sandbox script not found!"}
    
    # Формируем команду: safe-sandbox.sh "<команда>"
    safe_cmd = [SANDBOX_SCRIPT, command]
    
    try:
        result = subprocess.run(
            safe_cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30  # 🛡️ Защита от зависаний (DoS)
        )
        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except subprocess.TimeoutExpired:
        return {"returncode": -1, "stderr": "Команда превысила лимит времени (30с) и была прервана."}
    except Exception as e:
        return {"returncode": 1, "stderr": f"Критическая ошибка шлюза: {str(e)}"}

if __name__ == "__main__":
    # Тестовый запуск для проверки целостности
    print("🧪 Тест безопасного шлюза (file_gate)...")
    res = execute_safely("echo 'Данные защищены. Я внутри песочницы.' && ls -la ~")
    print(f"🔹 Код возврата: {res['returncode']}")
    print(f"🔹 Вывод:\n{res['stdout']}")
    if res['stderr']:
        print(f"🔹 Ошибки:\n{res['stderr']}")
