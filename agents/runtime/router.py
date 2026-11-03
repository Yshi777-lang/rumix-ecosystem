#!/data/data/com.termux/files/usr/bin/env python3
"""
router.py — rule-based выбор агента.

Правило: специфичные ключи ВЫШЕ. Общие — НИЖЕ.
Первое совпадение выигрывает.
"""

ROUTES = [
    # ─── debugger ───
    ("не работает",  "debugger"),
    ("падает",       "debugger"),
    ("ошиб",         "debugger"),
    ("баг",          "debugger"),

    # ─── reviewer (конкретные фразы) ───
    ("проверь код",  "reviewer"),
    ("проверь этот", "reviewer"),
    ("ревью",        "reviewer"),
    ("review",       "reviewer"),

    # ─── architect ───
    ("спроект",      "architect"),
    ("архитект",     "architect"),
    ("design",       "architect"),

    # ─── fury ───
    ("аудит",        "fury"),
    ("периметр",     "fury"),
    ("security",     "fury"),
    ("безопас",      "fury"),
    ("порт",         "fury"),

    # ─── liza ───
    ("хрон",         "liza"),
    ("запиши",       "liza"),
    ("истор",        "liza"),
    ("дата",         "liza"),

    # ─── neon (общее — в конце) ───
    ("скрипт",       "neon"),
    ("напиши",       "neon"),
    ("сделай",       "neon"),
    ("bash",         "neon"),
    ("python",       "neon"),
    ("код",          "neon"),
]

DEFAULT_AGENT = "neon"


def dispatch(task):
    t = task.lower()
    for key, agent in ROUTES:
        if key in t:
            return agent
    return DEFAULT_AGENT


if __name__ == "__main__":
    tests = [
        "напиши скрипт backup.sh",
        "проверь порт 8080",
        "запиши в хронику: сделали backup",
        "спроектируй систему агентов",
        "проверь этот код",
        "почему падает приложение",
        "как дела?",
    ]
    print("🔍 Тесты router.py:")
    for task in tests:
        agent = dispatch(task)
        print(f"  {task:45s} → {agent}")
