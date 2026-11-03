"""battery.py — заряд, температура и здоровье АКБ."""
import json
import subprocess
from core.modules import module, ModuleResult

m = module("battery", "Батарея", "🔋", "Заряд и здоровье АКБ (termux-api), опрос только по запросу.")

@m.get
def state():
    """Читает данные батареи через termux-api."""
    try:
        # Запускаем termux-battery-status с таймаутом
        r = subprocess.run(
            ["termux-battery-status"],
            capture_output=True, text=True, timeout=5
        )
        if r.returncode != 0:
            raise RuntimeError(r.stderr.strip() or "Ошибка termux-api")
            
        data = json.loads(r.stdout)
        return ModuleResult(
            data={
                "percentage": data.get("percentage"),
                "status": data.get("status", "unknown"),
                "temperature_c": data.get("temperature"),
                "health": data.get("health")
            },
            confidence="high"
        )
    except FileNotFoundError:
        return ModuleResult(
            data={"status": "unavailable"},
            status="unavailable",
            confidence="none",
            limitations=["termux-api не установлен: pkg install termux-api + приложение Termux:API с F-Droid"]
        )
    except subprocess.TimeoutExpired:
        return ModuleResult(
            data={"status": "timeout"},
            status="error",
            confidence="none",
            limitations=["termux-api не ответил за 5 секунд"]
        )
    except Exception as e:
        return ModuleResult(
            data={"status": "error", "message": str(e)},
            status="error",
            code=500,
            confidence="none"
        )
