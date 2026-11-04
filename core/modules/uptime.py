"""uptime.py — аптайм телефона (сколько не перезагружался)."""
import subprocess
from core.modules import module, ModuleResult

m = module("uptime", "Аптайм", "⏱️", "Сколько телефон не перезагружался.")

@m.get
def state():
    try:
        # uptime -p показывает "up 2 days, 3 hours"
        r = subprocess.run(["uptime", "-p"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            text = r.stdout.strip().replace("up ", "")
            return ModuleResult({"uptime": text})
        
        # fallback: читаем /proc/uptime (секунды)
        with open("/proc/uptime", "r") as f:
            seconds = float(f.read().split()[0])
            days = int(seconds // 86400)
            hours = int((seconds % 86400) // 3600)
            return ModuleResult({"uptime": f"{days} дней, {hours} часов"})
    except Exception as e:
        return ModuleResult({"error": str(e)}, code=500)
