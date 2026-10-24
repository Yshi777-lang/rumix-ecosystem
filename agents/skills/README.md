# Skills — навыки дома Rumix

**Дата создания:** 03.10.2026
**Референс:** Termux Ultra PluginDevSpec + Anthropic Agent Skills.

## Формат SKILL.md

Каждый skill — папка с SKILL.md:

skills/
├── linux-audit/
│   └── SKILL.md
├── network-audit/
│   └── SKILL.md
└── log-analysis/
    └── SKILL.md

## SKILL.md — структура

---
name: linux-audit
description: Аудит локальной конфигурации Linux/Android
tools: [system_info, package_info, network_status]
output: [RISKS, FINDINGS, RECOMMENDATIONS]
---

# Linux Audit

Инструкции для агента...

## Что делать

1. Собрать system_info.
2. Проверить подозрительные пакеты.
3. Оценить сеть.

## Output

RISKS/FINDINGS/RECOMMENDATIONS.
