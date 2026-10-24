---
name: network-audit
description: Аудит сети. Интерфейсы, DNS, порты, DNS-разведка доменов.
tools:
  - network_status
  - dns_lookup
output:
  - RISKS
  - FINDINGS
  - RECOMMENDATIONS
keywords:
  - сеть
  - network
  - dns
  - порт
  - port
  - интерфейс
  - interface
  - пинг
  - ping
  - wifi
---

# Network Audit

Скилл для аудита сети и DNS.

## Когда применять

- Задача содержит: «сеть», «network», «DNS», «dns», «порты», «интерфейсы».
- Пользователь просит проверить сеть или DNS.

## Шаги

1. **Собрать данные**:
   - `network_status` — интерфейсы, DNS, порты, ping.
   - `dns_lookup` — A/NS записи домена.

2. **Анализ**:
   - **FINDINGS** — факты: интерфейсы, DNS-серверы, ping, NS.
   - **RISKS** — риски: блокировка DNS, отсутствие резервных DNS, IPv6-only.
   - **RECOMMENDATIONS** — действия.

## Пример

**FINDINGS:**
- `[network_status] interfaces: lo, seth_lte0`
- `[network_status] dns: 8.8.8.8, 8.8.4.4`
- `[network_status] ping_8_8_8_8: 95.4 ms`
- `[dns_lookup] a: example.com → 8.47.69.6, 8.6.112.6`

**RISKS:**
- `[network_status] DNS 8.8.8.8 — может блокироваться в регионе`
- `[network_status] DNS 8.8.4.4 — Google резервный, но тоже может быть недоступен`

**RECOMMENDATIONS:**
- Рассмотреть альтернативные DNS (1.1.1.1, 9.9.9.9).
- Проверить наличие VPN/прокси для критичных операций.

## Output

Строго: RISKS / FINDINGS / RECOMMENDATIONS.
