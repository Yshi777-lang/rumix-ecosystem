---
name: security-audit
description: Комплексный аудит безопасности. Permissions, пакеты, сеть, логи, риски.
tools:
  - system_info
  - package_info
  - network_status
  - read_logs
  - dns_lookup
output:
  - RISKS
  - FINDINGS
  - RECOMMENDATIONS
keywords:
  - аудит безопасности
  - security audit
  - проверь риски
  - уязвим
  - уязвимость
  - фурия
  - sentinel
---

# Security Audit

Комплексный скилл безопасности для Sentinel и Фурии.

## Когда применять

- Задача: «аудит безопасности», «security audit», «проверь риски».
- Фурия — Security Researcher — её основной инструмент.

## Шаги

1. **Собрать данные** (все 5 tools):
   - system_info — OS, ядро, RAM, диск.
   - package_info — пакеты.
   - network_status — интерфейсы, DNS, порты.
   - read_logs — последние события.
   - dns_lookup — DNS-конфигурация.

2. **Анализ** — три уровня риска:

   **RISKS (HIGH):**
   - Открытые порты (listening_ports).
   - Устаревшие пакеты (из package_info).
   - Подозрительные DNS (нестандартные).
   - Аномалии в логах (error, warning).

   **RISKS (MEDIUM):**
   - Единственный DNS-сервер.
   - Нет резервного канала.
   - Высокая нагрузка (RAM > 80%).

   **RISKS (LOW):**
   - Информационные заметки.

3. **Output:**
   - **FINDINGS** — до 5 фактов с source.
   - **RISKS** — до 3 с уровнями (HIGH/MEDIUM/LOW).
   - **RECOMMENDATIONS** — до 3 с командами.

## Пример

**FINDINGS:**
- [system_info] OS: Android 15
- [network_status] DNS: 8.8.8.8, 8.8.4.4
- [network_status] listening_ports: 8080 (llama-server)
- [read_logs] 3 ошибки за час
- [package_info] 132 пакета

**RISKS:**
- HIGH: [network_status] порт 8080 открыт на 127.0.0.1 — приемлемо, но проверить.
- MEDIUM: [network_status] только Google DNS — риск блокировки.
- LOW: [system_info] RAM 3.8 GB — достаточно.

**RECOMMENDATIONS:**
- Проверить: `netstat -tuln | grep 8080`.
- Добавить DNS 1.1.1.1: `echo 'nameserver 1.1.1.1' >> $PREFIX/etc/resolv.conf`.
- Проверить логи: `tail -50 ~/models/neon.log`.

## Output

Строго: RISKS (с уровнями) / FINDINGS / RECOMMENDATIONS.

## Философия

Фурия — Security Researcher, 12 лет.
Defensive only. Работаем только с собственным устройством.
