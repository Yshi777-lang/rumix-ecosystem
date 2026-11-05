"""services.py — управление процессами дома из Shell."""

import shlex
import subprocess
from pathlib import Path

from core.modules import ModuleResult, module

m = module("services", "Сервисы", "⚙️", "Управление Shell, Неоном и Scanner.")


def _script() -> Path:
    """svc-manager.sh: сначала рядом с репозиторием, потом классический путь."""
    local = Path(__file__).resolve().parents[2] / "scripts" / "svc-manager.sh"
    if local.exists():
        return local
    return Path.home() / "rumix-ecosystem" / "scripts" / "svc-manager.sh"


def _run(cmd, timeout=25):
    script = _script()
    if not script.exists():
        return f"Ошибка: не найден {script}"
    try:
        r = subprocess.run(
            ["bash", str(script)] + cmd,
            capture_output=True, text=True, timeout=timeout,
        )
        out = r.stdout.strip()
        err = r.stderr.strip()
        return out + ("\n" + err if err else "")
    except subprocess.TimeoutExpired:
        return f"Ошибка: svc-manager не ответил за {timeout} с"
    except Exception as e:
        return f"Ошибка: {e}"


def _stop_detached(svc: str) -> None:
    """Остановка после ответа: 2 секунды, своя сессия, без наследования stdout."""
    script = _script()
    subprocess.Popen(
        ["bash", "-c", f"sleep 2; bash {shlex.quote(str(script))} stop {shlex.quote(svc)}"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
        close_fds=True,
    )


@m.get
def state():
    """Статус всех сервисов."""
    out = _run(["status"])
    return ModuleResult({"status_report": out})


@m.post
def action(data):
    """POST {"action": "start|stop", "svc": "shell|neon|scanner|all"}"""
    act = data.get("action")
    svc = data.get("svc", "all")

    if act not in ("start", "stop"):
        return ModuleResult({"error": "action должен быть 'start' или 'stop'"}, code=400)
    if svc not in ("shell", "neon", "scanner", "all"):
        return ModuleResult(
            {"error": "svc должен быть 'shell', 'neon', 'scanner' или 'all'"}, code=400
        )

    if act == "stop":
        _stop_detached(svc)
        return ModuleResult({
            "result": f"Остановка «{svc}» запущена (через 2 с).",
            "status": "partial",
            "limitations": ["остановка асинхронная: подтверждение — в следующем status"],
        })

    out = _run([act, svc])
    return ModuleResult({"result": out})
