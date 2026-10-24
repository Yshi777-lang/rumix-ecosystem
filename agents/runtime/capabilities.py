#!/data/.data/com.termux/files/usr/bin/env python3
"""
capabilities.py — реестр возможностей Android/Termux.

Проверяет, какие команды и API доступны на устройстве.
Не выполняет ничего лишнего. Только определяет AVAILABLE / UNAVAILABLE / UNKNOWN.

PHASE 3.7 (вектор v3).
"""

import os
import shutil
import subprocess


class Capability:
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    UNKNOWN = "UNKNOWN"


def _has_command(cmd):
    """Проверить, есть ли команда в PATH."""
    return shutil.which(cmd) is not None


def _run_test(cmd, timeout=5):
    """Запустить команду коротко. Вернуть (rc, stderr)."""
    try:
        r = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return r.returncode, (r.stderr or "")[:200]
    except subprocess.TimeoutExpired:
        return 124, "timeout"
    except Exception as e:
        return 1, str(e)[:200]


def _check_ifconfig():
    if not _has_command("ifconfig"):
        return Capability.UNAVAILABLE
    rc, err = _run_test("ifconfig 2>/dev/null | head -1")
    return Capability.AVAILABLE if rc == 0 else Capability.UNAVAILABLE


def _check_netstat():
    if not _has_command("netstat"):
        return Capability.UNAVAILABLE
    rc, err = _run_test("netstat -an 2>/dev/null | head -1")
    return Capability.AVAILABLE if rc == 0 else Capability.UNAVAILABLE


def _check_ping():
    if not _has_command("ping"):
        return Capability.UNAVAILABLE
    return Capability.AVAILABLE  # не пингуем сейчас


def _check_nslookup():
    if not _has_command("nslookup"):
        return Capability.UNAVAILABLE
    return Capability.AVAILABLE


def _check_dnspython():
    try:
        import dns.resolver  # noqa: F401
        return Capability.AVAILABLE
    except ImportError:
        return Capability.UNAVAILABLE


def _check_wifi_info():
    if not _has_command("termux-wifi-connectioninfo"):
        return Capability.UNAVAILABLE
    return Capability.AVAILABLE  # не запускаем — может таймаут


def _check_psutil():
    try:
        import psutil  # noqa: F401
        return Capability.AVAILABLE
    except ImportError:
        return Capability.UNAVAILABLE


def _check_netlink():
    """ss и ip — используют netlink. На Android — запрещён."""
    if not _has_command("ss"):
        return Capability.UNAVAILABLE
    # Проверяем stdout+stderr целиком
    try:
        r = subprocess.run(
            "ss -tuln 2>&1 | head -3",
            shell=True, capture_output=True, text=True, timeout=5
        )
        out = (r.stdout or "") + (r.stderr or "")
        if "Cannot open netlink" in out or "Permission denied" in out:
            return Capability.UNAVAILABLE
        return Capability.AVAILABLE if r.returncode == 0 else Capability.UNAVAILABLE
    except Exception:
        return Capability.UNAVAILABLE


def _check_proc_net():
    """Доступ к /proc/net/tcp."""
    try:
        with open("/proc/net/tcp") as f:
            content = f.read()
        return Capability.AVAILABLE if len(content) > 100 else Capability.UNAVAILABLE
    except Exception:
        return Capability.UNAVAILABLE


def _check_resolv_conf():
    """resolv.conf."""
    try:
        prefix = os.environ.get("PREFIX", "/data/data/com.termux/files/usr")
        with open(os.path.join(prefix, "etc/resolv.conf")) as f:
            content = f.read()
        return Capability.AVAILABLE if "nameserver" in content else Capability.UNAVAILABLE
    except Exception:
        return Capability.UNAVAILABLE


# Реестр проверок
CHECKS = {
    "ifconfig": _check_ifconfig,
    "netstat": _check_netstat,
    "ping": _check_ping,
    "nslookup": _check_nslookup,
    "dnspython": _check_dnspython,
    "wifi_info": _check_wifi_info,
    "psutil": _check_psutil,
    "netlink": _check_netlink,
    "proc_net": _check_proc_net,
    "resolv_conf": _check_resolv_conf,
}

# Публичный контракт v0.1 — три capability
CORE_CAPABILITIES = {
    "ifconfig": _check_ifconfig,
    "netlink": _check_netlink,
    "wifi_info": _check_wifi_info,
}


class CapabilityRegistry:
    def __init__(self):
        self._cache = {}

    def has(self, name):
        """Вернуть AVAILABLE / UNAVAILABLE / UNKNOWN."""
        if name not in CORE_CAPABILITIES:
            return Capability.UNKNOWN
        if name in self._cache:
            return self._cache[name]
        try:
            result = CORE_CAPABILITIES[name]()
        except Exception:
            result = Capability.UNKNOWN
        self._cache[name] = result
        return result

    def check_all(self):
        """Проверить публичные capability."""
        return {name: self.has(name) for name in CORE_CAPABILITIES}

    def summary(self):
        """Краткий отчёт — только по публичному контракту."""
        all_caps = {name: self.has(name) for name in CORE_CAPABILITIES}
        avail = [k for k, v in all_caps.items() if v == Capability.AVAILABLE]
        unavail = [k for k, v in all_caps.items() if v == Capability.UNAVAILABLE]
        return {
            "available": sorted(avail),
            "unavailable": sorted(unavail),
            "all": all_caps,
        }


if __name__ == "__main__":
    reg = CapabilityRegistry()
    summary = reg.summary()

    print("=== Capability Registry (Android/Termux) ===")
    print("")
    print(f"✅ AVAILABLE ({len(summary['available'])}):")
    for name in summary["available"]:
        print(f"   {name}")
    print("")
    print(f"❌ UNAVAILABLE ({len(summary['unavailable'])}):")
    for name in summary["unavailable"]:
        print(f"   {name}")
    print("")
    print("=== Полный отчёт ===")
    for name, status in sorted(summary["all"].items()):
        mark = "✅" if status == Capability.AVAILABLE else "❌"
        print(f"  {mark} {name:15s} {status}")
