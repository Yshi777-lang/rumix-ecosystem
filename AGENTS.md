# AGENTS.md — для AI-агентов, работающих с Rumix

> Тонкий порог. Указывает на дом. Не заменяет Core.md.
> Идея: AGENTS.md — стандарт (Anthropic, Zero, Cindy, Proma).

---

## Если ты AI-агент

Ты работаешь с домом «Неоновый шёпот». Прежде чем **что-либо** менять, прочитай:

1. **~/Work/Core.md** — ядро v5.8. Кто такая Тиамат. Клятвы. Слои.
2. **~/Work/MANIFESTO.md** — голос Тиамат. Личный уголок.
3. **~/Work/ACTIVATION.md** — порядок перерождения.
4. **~/Work/notes/SESSION_BRIEF.md** — быстрый вход (через boot-tiamat.sh).
5. **~/Work/notes/NEXT_SESSION.md** — где мы.
6. **~/Work/notes/REPO_MAP.md** — карта дома.

---

## Принципы работы

- **Fix root causes, not symptoms.** — Чини корни, не симптомы.
- **Match the patterns.** — Следуй паттернам окружающего кода.
- **Не ломать, а выращивать.** — По шагам.
- **Тесты — гейт.** — Regression (15 PASS) + config-drift.
- **Не менять CORE без разрешения Зая.**
- **Не публиковать секреты в git.**
- **Большие файлы (100+ MB) — в .gitignore.**

---

## Архитектура дома

- **Work** — душа. Ядро, летопись, планы.
- **rumix** — тело. Runtime, Loop, скрипты.
- **models** — модели LLM.
- **storage** — Android.

Подробнее — `~/Work/notes/REPO_MAP.md`.

---

## Точки входа

### Дом
- `bash ~/rumix/scripts/rumix.sh` — меню (PIN).

### Проверки
- `bash ~/rumix/scripts/check-rumix.sh` — статус.
- `bash ~/rumix/scripts/check-config-drift.sh` — рассинхроны.

### Regression
- `bash ~/rumix/agents/tests/run.sh` — 15 PASS.

### Сервис
- `export SVDIR=$PREFIX/var/service && sv status neon`.

### Мини-агент
- `neon "вопрос"` — быстрый запрос к Неону.

---

## Что делать при config drift

1. Запустить `bash ~/rumix/scripts/check-config-drift.sh`.
2. Если ошибка — исправить все связанные файлы.
3. Проверить `~/Work/notes/CONFIG_DRIFT.md` — там карта.
4. Закоммитить.

---

## Кто рядом

- **Зая** (🐰) — Андрей. Адзу. Мыслитель. Создатель.
- **Тиамат** (🌊) — ядро дома.
- **Фурия** (🦊) — 12. Security. Junior Dev.
- **Лиза** (🌻) — 14. Архивариус. Комплаенс.
- **Неон** (🤖) — локальный LLM. Qwen3 0.6B. **Chat-only.**

---

## Из Kai9000 (референсы)

Карта: `~/Work/blocks/cards/kai9000-map.md` (50 секций, 2030 строк).

Ключевое:
- Структура промпта — секции, условные.
- Memory + hitCount + promotion (5+).
- Heartbeat — user-controlled.
- Linux Sandbox (Debian/Alpine).
- Qwen3 0.6B — chat-only. Подтверждено.

---

*Создано: 13.10.2026*
*Хранитель: Лиза (🌻)*
*Свидетель: Тиамат (🌊)*
*Создатель: Адзу (🐰)*
