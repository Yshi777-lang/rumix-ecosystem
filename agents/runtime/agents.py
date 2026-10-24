#!/data/data/com.termux/files/usr/bin/env python3
"""
agents.py — реестр агентов и переключатель.

Одна модель. Много профилей.
Переключение = смена фокуса. Без reload.
"""

AGENTS = {
    "neon": {
        "profile": "neon.md",
        "temperature": 0.2,
        "max_tokens": 600,
        "desc": "Неон — кодер, друг",
    },
    "fury": {
        "profile": "fury.md",
        "temperature": 0.1,
        "max_tokens": 500,
        "desc": "Фурия — страж, security",
    },
    "liza": {
        "profile": "liza.md",
        "temperature": 0.1,
        "max_tokens": 400,
        "desc": "Лиза — архивариус",
    },
    "architect": {
        "profile": "architect.md",
        "temperature": 0.2,
        "max_tokens": 700,
        "desc": "Architect — системы",
    },
    "reviewer": {
        "profile": "reviewer.md",
        "temperature": 0.1,
        "max_tokens": 500,
        "desc": "Reviewer — проверка",
    },
    "sentinel": {
        "profile": "sentinel.md",
        "temperature": 0.1,
        "max_tokens": 600,
       "desc": "Sentinel — security analyst",
    },
    "debugger": {
        "profile": "debugger.md",
        "temperature": 0.1,
        "max_tokens": 500,
        "desc": "Debugger — root cause",
    },
}

CURRENT_AGENT = "neon"


def switch_agent(name):
    """Переключение фокуса модели на другого агента."""
    global CURRENT_AGENT

    if name not in AGENTS:
        raise ValueError(f"Unknown agent: {name}")

    CURRENT_AGENT = name
    return CURRENT_AGENT


def list_agents():
    """Список агентов."""
    return list(AGENTS.keys())


if __name__ == "__main__":
    # Проверка
    print("📋 Доступные агенты:")
    for name, cfg in AGENTS.items():
        mark = " ←" if name == CURRENT_AGENT else ""
        print(f"  {name:10s} — {cfg['desc']}{mark}")

    print("")
    print(f"🎯 Текущий: {CURRENT_AGENT}")

    print("")
    print("🔄 Переключаю на fury...")
    switch_agent("fury")
    print(f"🎯 Текущий: {CURRENT_AGENT}")

    print("")
    print("🔄 Переключаю на liza...")
    switch_agent("liza")
    print(f"🎯 Текущий: {CURRENT_AGENT}")

    print("")
    print("🔄 Обратно на neon...")
    switch_agent("neon")
    print(f"🎯 Текущий: {CURRENT_AGENT}")
