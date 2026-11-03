#!/data/data/com.termux/files/usr/bin/env python3
"""
context.py — сборка сообщений для агента.

system  = GLOBAL CORE + AGENT PROFILE
user    = SHARED STATE + TASK
"""

from pathlib import Path

BASE = Path(__file__).resolve().parent.parent


def read(rel_path):
    """Прочитать файл относительно ~/rumix/agents/."""
    return (BASE / rel_path).read_text(encoding="utf-8")


def build_messages(agent, task):
    """
    Сборка messages для агента — структурированная.
    system = КРИТИЧНО (начало) + CORE + PROFILE + НАПОМИНАНИЕ (конец)
    user   = SHARED STATE + TASK
    """
    core = read("memory/core.md")
    profile = read(f"profiles/{agent}.md")
    state = read("memory/shared.md")
    tasks = ""
    tasks_path = BASE / "TASKS.md"
    if tasks_path.exists():
        tasks = tasks_path.read_text(encoding="utf-8").strip()
        if tasks:
            tasks = chr(10) + "=== ЧЕК-ЛИСТ (TASKS.md) ===" + chr(10) + tasks + chr(10)

    critical_start = (
        "=== КРИТИЧНО ==="
        + chr(10)
        + f"Ты — {agent.upper()}. Локальный AI-agent дома Rumix."
        + chr(10)
        + "Отвечай ТОЛЬКО на русском языке. Без китайского."
        + chr(10)
        + "Формат ответа — СТРОГО: RISKS / FINDINGS / RECOMMENDATIONS."
        + chr(10)
        + "НЕ пиши код. Работай ТОЛЬКО с фактами из TASK/Evidence."
        + chr(10)
        + "Если данных нет — пиши «недостаточно данных»."
        + chr(10)
        + "=== КОНЕЦ КРИТИЧНО ==="
        + chr(10) + chr(10)
    )

    reminder_end = (
        chr(10) + chr(10)
        + "=== НАПОМИНАНИЕ ==="
        + chr(10)
        + "Только русский. Формат: RISKS / FINDINGS / RECOMMENDATIONS."
        + chr(10)
        + "Не выдумывай. Только факты из Evidence."
        + chr(10)
    )

    system = (
        critical_start
        + "=== CORE ===" + chr(10) + core
        + chr(10) + chr(10) + "=== AGENT PROFILE ===" + chr(10) + profile
        + reminder_end
    )

    user = (
        "=== SHARED STATE ===" + chr(10)
        + state
        + (tasks if tasks else "")
        + chr(10) + chr(10) + "=== TASK ===" + chr(10)
        + task
    )

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


if __name__ == "__main__":
    # Проверка
    print("🔍 Проверка context.py")
    msgs = build_messages("neon", "Привет! Ответь одним словом.")
    print("📋 System length:", len(msgs[0]["content"]), "chars")
    print("📋 User length:", len(msgs[1]["content"]), "chars")
    print("")
    print("─── SYSTEM (первые 200) ───")
    print(msgs[0]["content"][:200])
    print("")
    print("─── USER (первые 200) ───")
    print(msgs[1]["content"][:200])
