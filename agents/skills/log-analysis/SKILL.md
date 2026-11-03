---
name: log-analysis
description: Анализ логов. Поиск ошибок, паттернов, аномалий.
tools:
  - read_logs
  - run_command
output:
  - RISKS
  - FINDINGS
  - RECOMMENDATIONS
keywords:
  - лог
  - log
  - ошиб
  - error
  - сбой
  - daemon
  - анализ
  - аналитик
---

# Log Analysis

Скилл для анализа логов и выявления проблем.

## Когда применять

- Задача содержит: «лог», «log», «ошибки», «сбой», «daemon».
- Пользователь просит проверить логи.

## Шаги

1. **Собрать данные**:
   - `read_logs` — последние строки логов (санитизированные).
   - `run_command` — `grep`, `awk`, `sort` для анализа.

2. **Анализ**:
   - **FINDINGS** — факты: ошибки, предупреждения, частые паттерны.
   - **RISKS** — риски: пропущенные сервисы, повторяющиеся ошибки.
   - **RECOMMENDATIONS** — что чинить.

## Пример

**FINDINGS:**
- `[read_logs] daemon.log: 3 ошибки за 5 минут`
- `[read_logs] [PERM] warnings: 12`
- `[run_command] top-5 grep: error, warning, skip, perm, timeout`

**RISKS:**
- `[read_logs] Повторяющиеся PERM warnings — возможна проблема прав`
- `[read_logs] Skip логов — потеря диагностики`

**RECOMMENDATIONS:**
- Проверить права на лог-файлы.
- Включить логирование для пропущенных категорий.

## Output

Строго: RISKS / FINDINGS / RECOMMENDATIONS.
