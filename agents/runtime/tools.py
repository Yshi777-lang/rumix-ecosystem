#!/data/data/com.termux/files/usr/bin/env python3
"""
tools.py — ToolRegistry с Tool Contract.

Контракт: name, description, input_schema, handler,
permissions (READ/WRITE/EXEC/NETWORK), output_schema.
Принцип: Tool → данные. Agent → анализ. Runtime → orchestration.
"""

import os
import platform
import shutil
import subprocess

from runtime.permissions import Permission, check as perm_check
from runtime.capabilities import CapabilityRegistry, Capability
from runtime.sanitizer import sanitize

CAPS = CapabilityRegistry()


def _run(cmd, timeout=10):
    """Безопасный запуск команды, возвращает stdout."""
    try:
        r = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return r.stdout.strip() or r.stderr.strip()
    except subprocess.TimeoutExpired:
        return f"[timeout: {timeout}s]"
    except Exception as e:
        return f"[error: {e}]"


def handler_system_info():
    """Собрать базовую информацию о системе."""
    info = {
        "os": platform.system(),
        "os_release": platform.release(),
        "machine": platform.machine(),
        "python": platform.python_version(),
        "prefix": os.environ.get("PREFIX", "не задан"),
        "home": os.environ.get("HOME", "не задан"),
        "cpu_cores": os.cpu_count(),
    }
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    info["ram_total_kb"] = line.split(":")[1].strip().split()[0]
                if line.startswith("MemAvailable:"):
                    info["ram_available_kb"] = line.split(":")[1].strip().split()[0]
    except Exception:
        pass
    try:
        total, used, free = shutil.disk_usage(os.path.expanduser("~"))
        info["disk_total_gb"] = round(total / 1024**3, 1)
        info["disk_free_gb"] = round(free / 1024**3, 1)
    except Exception:
        pass
    return info


def handler_package_info(pkg_name=None):
    """Информация о пакетах Termux (dpkg)."""
    if pkg_name:
        out = _run(f"dpkg -s {pkg_name}")
        info = {}
        for line in out.splitlines():
            if ": " in line:
                k, v = line.split(": ", 1)
                if k in ("Package", "Version", "Status", "Architecture",
                         "Installed-Size", "Maintainer", "Description"):
                    info[k.lower()] = v.strip()
        return info if info else {"error": f"package not found: {pkg_name}"}

    out = _run("dpkg-query -W -f='${Package} ${Version}\\\\n' 2>/dev/null")
    packages = {}
    for line in out.splitlines():
        parts = line.split(None, 1)
        if len(parts) == 2:
            packages[parts[0]] = parts[1]
    top = dict(list(packages.items())[:15])
    return {
        "count": len(packages),
        "top_15": top,
    }


def handler_network_status():
    """Информация о сети: интерфейсы, маршруты, DNS, порты, ping, WiFi."""
    info = {}

    # Интерфейсы — через ifconfig, если доступно
    interfaces = {}
    if CAPS.has("ifconfig") == Capability.AVAILABLE:
        out = _run("ifconfig 2>/dev/null")
        current = None
        for line in out.splitlines():
            if line and not line[0].isspace():
                current = line.split(":")[0].split()[0]
                interfaces[current] = {}
            elif current:
                line = line.strip()
                if line.startswith("inet "):
                    interfaces[current]["ipv4"] = line.split()[1]
                elif line.startswith("inet6 "):
                    interfaces[current]["ipv6"] = line.split()[1]
                elif line.startswith("ether "):
                    interfaces[current]["mac"] = line.split()[1]
    else:
        # Fallback: только loopback через socket
        try:
            import socket
            interfaces["lo"] = {"ipv4": "127.0.0.1"}
        except Exception:
            pass
    info["interfaces"] = interfaces

    # Маршруты — недоступны на Android (netlink запрещён, netstat -rn пусто)
    info["routes"] = []

    # DNS
    dns = []
    try:
        resolv = os.path.join(os.environ.get("PREFIX", "/data/data/com.termux/files/usr"), "etc/resolv.conf")
        with open(resolv) as f:
            for line in f:
                if line.startswith("nameserver"):
                    dns.append(line.split()[1])
    except Exception:
        pass
    info["dns"] = dns

    # Порты — недоступны на Android (netlink запрещён, netstat -tuln не поддерживает TCP)
    info["listening_ports"] = []

    # Ping — через capability
    if CAPS.has("ping") == Capability.AVAILABLE:
        out = _run("ping -c 1 -W 2 8.8.8.8 2>/dev/null | grep -E 'time=|loss'", timeout=30)
        info["ping_8_8_8_8"] = out if out else "no response"
    else:
        info["ping_8_8_8_8"] = "unavailable (capability)"

    # WiFi — только если capability доступна
    if CAPS.has("wifi_info") == Capability.AVAILABLE:
        out = _run("termux-wifi-connectioninfo 2>/dev/null", timeout=5)
    else:
        out = ""
    if out and "not found" not in out:
        try:
            import json
            wifi = json.loads(out)
            info["wifi"] = {
                "ssid": wifi.get("ssid"),
                "ip": wifi.get("ip"),
                "link_speed_mbps": wifi.get("link_speed_mbps"),
                "frequency_mhz": wifi.get("frequency_mhz"),
            }
        except Exception:
            info["wifi"] = out[:200]

    # Capability info
    info["capabilities"] = {
        "netlink": CAPS.has("netlink"),
        "proc_net": CAPS.has("proc_net"),
        "wifi_info": CAPS.has("wifi_info"),
        "ifconfig": CAPS.has("ifconfig"),
        "ping": CAPS.has("ping"),
    }

    # Status — partial, если есть UNAVAILABLE
    unavail = [k for k, v in info["capabilities"].items() if v == Capability.UNAVAILABLE]
    info["status"] = "partial" if unavail else "full"

    return info


ALLOWED_LOG_DIRS = [
    os.path.expanduser("~/rumix/logs"),
    os.path.expanduser("~/models"),
]


def handler_read_logs(path=None, lines=5):
    """Чтение логов с санитизацией секретов.
    Если path не задан — ищет первый существующий лог.
    """
    if path is None:
        # Список кандидатов (первый существующий)
        candidates = [
            os.path.expanduser("~/models/neon.log"),
            os.path.expanduser("~/rumix/logs/daemon.log"),
            os.path.expanduser("~/rumix/logs/last_processed.txt"),
        ]
        path = None
        for c in candidates:
            if os.path.exists(c):
                path = c
                break
        if path is None:
            return {
                "error": "no logs found",
                "checked": candidates,
            }

    path = os.path.expanduser(path)
    real = os.path.realpath(path)

    allowed = any(real.startswith(os.path.realpath(d)) for d in ALLOWED_LOG_DIRS)
    if not allowed:
        return {"error": f"path not allowed: {path}", "allowed": ALLOWED_LOG_DIRS}

    if not os.path.exists(real):
        return {"error": f"file not found: {path}"}

    try:
        from collections import deque
        with open(real, "r", errors="replace") as f:
            tail = list(deque(f, maxlen=int(lines)))
        raw = "".join(tail)
        clean = sanitize(raw)
        return {"path": path, "lines": len(tail), "content": clean}
    except Exception as e:
        return {"error": f"read error: {e}"}


def handler_dns_lookup(domain, record_type="A", server="google", timeout=8):
    """DNS-разведка домена через dnspython (10 типов записей).

    record_type: A, AAAA, MX, TXT, CNAME, NS, SOA, PTR, SRV, CAA.
    server: system, google, cloudflare, opendns, quad9, или IP.
    """
    if not domain:
        return {"error": "domain required"}

    try:
        import dns.resolver
        import dns.exception
    except ImportError:
        return {"error": "dnspython не установлен. pip install dnspython"}

    # Серверы
    servers = {
        "system": None,
        "google": "8.8.8.8",
        "cloudflare": "1.1.1.1",
        "opendns": "208.67.222.222",
        "quad9": "9.9.9.9",
    }

    if server in servers:
        nameserver = servers[server]
    else:
        nameserver = server  # IP напрямую

    try:
        resolver = dns.resolver.Resolver(configure=(nameserver is None))
        if nameserver:
            resolver.nameservers = [nameserver]
        resolver.timeout = timeout
        resolver.lifetime = timeout

        record_type = record_type.upper()

        # PTR — обратный запрос
        if record_type == "PTR" and domain and not domain.endswith(".arpa"):
            import ipaddress
            try:
                addr = ipaddress.ip_address(domain)
                domain = addr.reverse_pointer
            except ValueError:
                pass

        import time
        t0 = time.time()
        answers = resolver.resolve(domain, record_type)
        query_ms = int((time.time() - t0) * 1000)

        records = []
        for rdata in answers:
            records.append({
                "type": record_type,
                "name": domain,
                "value": str(rdata).strip(),
                "ttl": answers.rrset.ttl if hasattr(answers, "rrset") else 0,
            })

        return {
            "domain": domain,
            "record_type": record_type,
            "server": nameserver or "system",
            "query_ms": query_ms,
            "rcode": "NOERROR",
            "records": records,
        }
    except dns.exception.Timeout:
        return {"error": f"timeout after {timeout}s", "domain": domain}
    except dns.resolver.NXDOMAIN:
        return {"domain": domain, "rcode": "NXDOMAIN", "records": []}
    except dns.resolver.NoAnswer:
        return {"domain": domain, "rcode": "NOERROR (empty)", "records": []}
    except Exception as e:
        return {"error": str(e), "domain": domain}

def handler_run_command(command, timeout=30, cwd=None, quiet=False, label=None):
    """Выполнить команду с проверкой риска.

    Градация: HIGH — отказ (до permissions), MEDIUM — спросить, LOW — выполнить.
    Дополнительно: cwd, quiet (LOG_LEVEL_OFF), label (метка для логов).
    """
    if not command or not isinstance(command, str):
        return {"error": "command required"}

    if label:
        print(f"[cmd:{label}] {command[:80]}")

    try:
        r = subprocess.run(
            command, shell=True, capture_output=True, text=True,
            timeout=timeout, cwd=cwd,
        )
        stdout = r.stdout[-2000:] if r.stdout else ""
        stderr = r.stderr[-500:] if r.stderr else ""

        result = {
            "command": command,
            "exit_code": r.returncode,
            "stdout": stdout,
            "stderr": stderr,
            "success": (r.returncode == 0),
        }
        if label:
            result["label"] = label
        if quiet:
            result.pop("stdout", None)
            result.pop("stderr", None)
        return result
    except subprocess.TimeoutExpired:
        return {"error": f"timeout after {timeout}s", "command": command, "success": False}
    except Exception as e:
        return {"error": str(e), "command": command, "success": False}


class Tool:
    def __init__(self, name, description, handler,
                 permissions=None, input_schema=None, output_schema=None,
                 required_capabilities=None, allow_partial=False):
        self.name = name
        self.description = description
        self.handler = handler
        self.permissions = permissions or [Permission.READ]
        self.input_schema = input_schema or {}
        self.output_schema = output_schema or {}
        self.required_capabilities = required_capabilities or []
        self.allow_partial = allow_partial

    def __repr__(self):
        perms = ",".join(p.value for p in self.permissions)
        return f"<Tool {self.name} [{perms}]>"

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "permissions": [p.value for p in self.permissions],
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "required_capabilities": self.required_capabilities,
        }


TOOL_REGISTRY = {
    "system_info": Tool(
        name="system_info",
        description="OS, ядро, CPU, RAM, диск, Termux prefix",
        handler=handler_system_info,
        permissions=[Permission.READ],
    ),
    "package_info": Tool(
        name="package_info",
        description="Список пакетов Termux (dpkg)",
        handler=handler_package_info,
        permissions=[Permission.READ],
        input_schema={"pkg_name": "str|None"},
    ),
    "network_status": Tool(
        name="network_status",
        description="Интерфейсы, маршруты, DNS, порты, ping",
        handler=handler_network_status,
        permissions=[Permission.READ, Permission.NETWORK],
        required_capabilities=["ifconfig", "wifi_info"],
        allow_partial=True,
    ),
    "read_logs": Tool(
        name="read_logs",
        description="Чтение логов (с санитизацией)",
        handler=handler_read_logs,
        permissions=[Permission.READ],
        input_schema={"path": "str|None", "lines": "int"},
    ),
    "dns_lookup": Tool(
        name="dns_lookup",
        description="DNS-разведка домена: A, NS",
        handler=handler_dns_lookup,
        permissions=[Permission.NETWORK],
        input_schema={
            "domain": "str",
            "record_type": "str",
            "server": "str",
            "timeout": "int",
        },
    ),
    "run_command": Tool(
        name="run_command",
        description="Выполнить shell-команду (с проверкой риска)",
        handler=handler_run_command,
        permissions=[Permission.EXEC],
        input_schema={
            "command": "str",
            "timeout": "int",
            "cwd": "str|None",
            "quiet": "bool",
            "label": "str|None",
        },
        output_schema={
            "command": "str",
            "exit_code": "int",
            "stdout": "str",
            "stderr": "str",
        },
    ),
}


def call_tool(tool_name, auto_approve=False, **kwargs):
    """Вызвать инструмент по имени."""
    if tool_name not in TOOL_REGISTRY:
        return {"error": f"Неизвестный инструмент: {tool_name}"}

    tool = TOOL_REGISTRY[tool_name]

    # Capability Check — FACT
    if tool.required_capabilities:
        from runtime.capabilities import CapabilityRegistry, Capability
        caps = CapabilityRegistry()
        blocked = None
        for cap_name in tool.required_capabilities:
            status = caps.has(cap_name)
            if status == Capability.UNAVAILABLE:
                blocked = ("capability_unavailable", cap_name)
                break
            elif status == Capability.UNKNOWN:
                blocked = ("capability_unknown", cap_name)
                break

        if blocked:
            err_code, cap_name = blocked
            if not tool.allow_partial:
                return {
                    "error": err_code,
                    "tool": tool_name,
                    "capability": cap_name,
                    "reason": f"Capability '{cap_name}' недоступна (или неизвестна)",
                }
            # allow_partial=True — пропускаем, handler сам решит

    # Передаём command в perm_check для проверки риска
    cmd = kwargs.get("command") if kwargs else None
    try:
        perm_check(tool.name, tool.permissions, auto_approve=auto_approve, command=cmd)
    except Exception as e:
        return {"error": f"Permission denied: {e}"}

    try:
        if kwargs:
            result = tool.handler(**kwargs)
        else:
            result = tool.handler()
    except Exception as e:
        return {"error": f"Ошибка в {tool_name}: {e}", "tool": tool_name}

    # HARDENING
    if result is None:
        return {"error": "empty result (None)", "tool": tool_name}
    if not isinstance(result, dict):
        return {"malformed": True, "raw": str(result)[:200], "tool": tool_name}
    if not result:
        return {"empty": True, "tool": tool_name}

    return result


def format_result(result):
    """Форматировать результат для LLM."""
    if isinstance(result, dict):
        lines = []
        for k, v in result.items():
            if isinstance(v, str) and "\n" in v:
                v = v.replace("\n", " | ")
            lines.append(f"  {k}: {v}")
        return "\n".join(lines)
    return str(result)


def list_tools():
    return [t.to_dict() for t in TOOL_REGISTRY.values()]


if __name__ == "__main__":
    print("=== ToolRegistry ===")
    for t in list_tools():
        print(f"  {t['name']} [{','.join(t['permissions'])}]")
    print()
    print("=== system_info() ===")
    print(format_result(call_tool("system_info", auto_approve=True)))
