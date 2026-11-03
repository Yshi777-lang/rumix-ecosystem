#!/data/data/com.termux/files/usr/bin/env python3
"""
netinfo.py — сетевая информация на Android с fallback.

Android закрывает /proc/net, psutil не работает.
Работает через: resolv.conf, subprocess, getprop.
"""

import os
import subprocess


def _run(cmd, timeout=10):
    """Безопасный запуск команды."""
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip() or r.stderr.strip()
    except Exception as e:
        return f"[error: {e}]"


def read_dns():
    """DNS из $PREFIX/etc/resolv.conf (работает на Android)."""
    dns = []
    try:
        prefix = os.environ.get("PREFIX", "/data/data/com.termux/files/usr")
        with open(os.path.join(prefix, "etc/resolv.conf")) as f:
            for line in f:
                if line.startswith("nameserver"):
                    dns.append(line.split()[1])
    except Exception:
        pass
    return dns


def read_dns_getprop():
    """DNS через getprop (fallback для Android)."""
    dns = []
    try:
        out = _run("getprop | grep -iE 'dns' | head -10")
        for line in out.splitlines():
            if "]: [" in line and "dns" in line.lower():
                value = line.split("]: [", 1)[1].rstrip("]")
                if value and value not in dns and "." in value:
                    dns.append(value)
    except Exception:
        pass
    return dns


def list_interfaces():
    """Интерфейсы через ifconfig (subprocess)."""
    interfaces = {}
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
    return interfaces


def list_listening_ports():
    """Слушающие порты через netstat (subprocess)."""
    ports = []
    out = _run("netstat -tuln 2>/dev/null | tail -n +3")
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 4:
            ports.append({"proto": parts[0], "local": parts[3]})
    return ports[:20]


def list_routes():
    """Маршруты через netstat -rn."""
    out = _run("netstat -rn 2>/dev/null | head -20")
    return out.splitlines() if out else []


def read_arp():
    """ARP через /proc/net/arp (на Android может быть пустым)."""
    arp = {}
    try:
        with open("/proc/net/arp") as f:
            lines = f.read().splitlines()
        for line in lines[1:]:
            parts = line.split()
            if len(parts) < 4:
                continue
            ip = parts[0]
            mac = parts[3].upper()
            if mac == "00:00:00:00:00:00":
                continue
            arp[ip] = mac
    except Exception:
        pass
    return arp


def get_dns(use_fallback=True):
    """DNS с fallback на getprop."""
    dns = read_dns()
    if not dns and use_fallback:
        dns = read_dns_getprop()
    return dns


if __name__ == "__main__":
    print("=== DNS ===")
    print(get_dns())
    print()
    print("=== Interfaces ===")
    ifaces = list_interfaces()
    for name, data in ifaces.items():
        print(f"  {name}: {data}")
    print()
    print("=== Listening ports ===")
    for p in list_listening_ports():
        print(f"  {p}")
    print()
    print("=== ARP ===")
    print(read_arp())
