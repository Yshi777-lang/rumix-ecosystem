#!/data/data/com.termux/files/usr/bin/env python3
"""Rumix Tools CLI — отладка tools через Python Fire.

Запуск:
    cd ~/rumix/agents
    python3 -m runtime.cli system_info
    python3 -m runtime.cli package_info
    python3 -m runtime.cli network_status
    python3 -m runtime.cli read_logs --lines=10
    python3 -m runtime.cli dns_lookup google.com --record_type=A
    python3 -m runtime.cli run_command --command="ls ~/rumix"

Установка Fire: pip install fire
"""

import sys
from pathlib import Path

# Добавляем корень agents в путь
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    import fire
except ImportError:
    print("❌ Нужен fire: pip install fire")
    sys.exit(1)

from runtime.tools import (
    handler_system_info,
    handler_package_info,
    handler_network_status,
    handler_read_logs,
    handler_dns_lookup,
    handler_run_command,
)


class Tools:
    """Rumix Tools — CLI для отладки."""

    def system_info(self):
        """Системная информация: OS, CPU, RAM, диск."""
        return handler_system_info()

    def package_info(self):
        """Информация о пакетах Termux."""
        return handler_package_info()

    def network_status(self):
        """Сетевой статус: интерфейсы, DNS, ping."""
        return handler_network_status()

    def read_logs(self, path=None, lines=5):
        """Читать логи (последние N строк)."""
        return handler_read_logs(path=path, lines=lines)

    def dns_lookup(self, domain, record_type="A", server="google", timeout=8):
        """DNS-разведка домена."""
        return handler_dns_lookup(
            domain=domain,
            record_type=record_type,
            server=server,
            timeout=timeout,
        )

    def run_command(self, command, timeout=30, label=None, quiet=False):
        """Выполнить команду (EXEC-tool)."""
        return handler_run_command(
            command=command,
            timeout=timeout,
            label=label,
            quiet=quiet,
        )


if __name__ == "__main__":
    fire.Fire(Tools)
