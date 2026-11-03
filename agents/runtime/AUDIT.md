# Model Path Audit — 05.10.2026

**Цель:** найти все пути к модели. Не менять. Только карта.

## Прямые вызовы api.ask()

- `orchestrator.py:13` — from runtime.api import ask
- `pipeline.py:15` — from runtime.api import ask
- `skill_dreamer.py:20` — from runtime.api import ask

## Проверки

- `main.py:28` — from runtime.api import health

## Provider (новый путь)

- `local_provider.py` — LocalProvider над api.py.
- `provider.py` — базовый ModelProvider.

## Прямые знания о llama-server

- `api.py:11` — SERVER = "http://127.0.0.1:8080/v1/chat/completions"
- `api.py:12` — MODELS_URL = "http://127.0.0.1:8080/v1/models"

## Что нужно

Прямые вызовы api.ask() → заменить на Provider.
Не удалять api.py. Сначала — новый путь, потом — решение.

## Что НЕ трогать

- Loop v0.5 (cache.jsonl, Pattern Detection).
- Tests (уже отдельные).

**Собрано:** 05.10.2026.


---

## Обновление: 06.10.2026 — после Integration Provider

**Model Path Audit — пройден.**

### Единственный вызов api.ask()
- `local_provider.py:21` — по дизайну. Provider path.

### Прямые вызовы api.ask() в Runtime — отсутствуют
- orchestrator.py — Provider ✅
- pipeline.py — Provider ✅
- skill_dreamer.py — Provider ✅

### Рабочий путь
Agent → Orchestrator → Provider → LocalProvider → api.py → llama-server → Qwen

### Legacy
- api.py — низкий уровень. Оставить. Backward compat.
- context.py.bak — .bak. Не используется.

### Вердикт
Победа 68 действительно закончена.

---

*Обновлено: 06.10.2026*


---

## Обновление: 08.10.2026 — Model Path Audit (69.5)

**Model Path Audit — пройден.**

### Прямые вызовы api.ask() в Runtime
- **Только** local_provider.py:21. По дизайну.
- orchestrator.py, pipeline.py, skill_dreamer.py — Provider.
- Provider v0.1 — закрыть.

### Классификация находок
- api.py — низкий уровень. Оставить.
- local_provider.py — единственный вызов api.ask(). Оставить.
- orchestrator, pipeline, skill_dreamer — provider.generate(req). OK.
- provider.py:60-61 — базовый метод. OK.
- test_07.sh — Mock. OK.
- main.py:143 — print. Не вызов.

### Мусор — удалён
- context.py.bak
- orchestrator.py.bak

### Вердикт
Provider v0.1 — закрыт. Следующий кирпич — Product Packaging Smoke Build (70).

---

*Обновлено: 08.10.2026*
