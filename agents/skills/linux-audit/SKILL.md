---
name: linux-audit
description: Аудит локальной конфигурации Linux/Android. Базовые проверки системы, пакетов, сети.
tools:
  - system_info
  - package_info
  - network_status
output:
  - RISKS
  - FINDINGS
  - RECOMMENDATIONS
keywords:
  - аудит
  - audit
  - безопас
  - security
  - систем
  - system
  - linux
  - android
  - конфиг
---

# Linux Audit

Скилл для аудита локальной системы.

## Когда применять

- Задача содержит: «аудит», «audit», «безопасность», «security», «система», «system».
- Пользователь просит проверить конфигурацию.

## Шаги

1. **Собрать данные**:
   - `system_info` — OS, ядро, CPU, RAM, диск.
   - `package_info` — установленные пакеты.
   - `network_status` — интерфейсы, DNS, порты.

2. **Анализ**:
   - **FINDINGS** — факты из собранных данных. Формат: `[source] ключ: значение`.
   - **RISKS** — интерпретация фактов. Что **может** **пойти** **не** **так**.
   - **RECOMMENDATIONS** — конкретные действия.

3. **Правила**:
   - Не дублировать RISKS и FINDINGS.
   - FINDINGS — только сырые данные.
   - RISKS — интерпретация + источник.
   - Не выдумывать. Если данных нет — «недостаточно данных для X».

## Пример

**FINDINGS:**
- `[system_info] OS: Android 15`
- `[system_info] CPU: 8 ядер`
- `[system_info] RAM: 3885420 KB`

**RISKS:**
- `[system_info] RAM 3.8ГБ — мало для LLM 7B, риск OOM`
- `[network_status] DNS 8.8.8.8 — может блокироваться в регионе`

**RECOMMENDATIONS:**
- Проверить логи на предмет ошибок.
- Рассмотреть альтернативные DNS.

## Output

Строго: RISKS / FINDINGS / RECOMMENDATIONS.
