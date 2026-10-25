"""
adb_manager.py — управление ADB для Rumix.
Обёртка над `adb` (Termux). Позволяет управлять телефоном: приложения, файлы, shell.
"""

import subprocess
from typing import List, Dict

PROTECTED = {
    "android", "com.android.systemui", "com.android.settings", "com.android.shell",
    "com.android.phone", "com.android.providers.settings", "com.android.providers.telephony",
    "com.android.permissioncontroller", "com.android.packageinstaller", "com.google.android.packageinstaller",
    "com.android.inputdevices", "com.android.server.telecom", "com.android.bluetooth",
    "app.adbphon",
}


class AdbManager:
    def __init__(self):
        self.is_connected = False

    def _run(self, args: List[str], timeout: int = 15) -> Dict:
        try:
            r = subprocess.run(["adb"] + args, capture_output=True, text=True, timeout=timeout)
            return {"ok": r.returncode == 0, "out": r.stdout.strip(), "err": r.stderr.strip()}
        except Exception as e:
            return {"ok": False, "out": "", "err": str(e)}

    def connect(self, host: str = "127.0.0.1", port: int = 5555) -> Dict:
        res = self._run(["connect", f"{host}:{port}"])
        self.is_connected = "connected" in res["out"].lower()
        return res

    def pair(self, host: str, port: int, code: str) -> Dict:
        return self._run(["pair", f"{host}:{port}", code])

    def shell(self, cmd: str) -> Dict:
        return self._run(["shell", cmd])

    def list_apps(self, system: bool = False) -> List[str]:
        cmd = "pm list packages" + (" -s" if system else "")
        res = self.shell(cmd)
        if not res["ok"]:
            return []
        return [l.replace("package:", "").strip() for l in res["out"].split("\n") if l.strip()]

    def install_apk(self, path: str) -> Dict:
        return self._run(["install", "-r", path], timeout=60)

    def action_app(self, pkg: str, action: str) -> Dict:
        if pkg in PROTECTED:
            return {"ok": False, "err": f"Пакет {pkg} защищён", "out": ""}
        mapping = {
            "disable": ["shell", "pm", "disable-user", "--user", "0", pkg],
            "enable": ["shell", "pm", "enable", pkg],
            "uninstall": ["uninstall", pkg],
            "stop": ["shell", "am", "force-stop", pkg],
            "clear": ["shell", "pm", "clear", pkg],
        }
        if action not in mapping:
            return {"ok": False, "err": f"Неизвестное действие: {action}", "out": ""}
        return self._run(mapping[action])
