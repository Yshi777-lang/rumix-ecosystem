#!/data/data/com.termux/files/usr/bin/env python3
"""
main.py — CLI для Agent Runtime (v2).

Подключён к orchestrator (full cycle): Router + Tools + Permission + Sanitizer + Evidence + FakeCheck + Report.

Команды:
  /agents              — список агентов
  /agent <name>        — переключить
  @<name> <task>       — переключить + выполнить (со tools)
  /tools               — список tools
  /skills              — список skills
  /report              — путь к последнему отчёту
  /model               — текущая модель
  /state               — состояние
  /help                — справка
  /quit                — выйти

Просто текст → full cycle через orchestrator.
"""

import sys
import os
import glob

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from runtime.api import health
from runtime.agents import AGENTS, switch_agent
from runtime.tools import list_tools
from runtime.orchestrator import run_agent_with_tools
import runtime.agents as agents_mod


def parse_inline(text):
    """@agent task — inline выбор."""
    if text.startswith("@"):
        parts = text.split(maxsplit=1)
        name = parts[0][1:]
        task = parts[1] if len(parts) > 1 else ""
        return name, task
    return None, text


def cmd_agents():
    print("=== Агенты ===")
    for name, cfg in AGENTS.items():
        mark = " ←" if name == agents_mod.CURRENT_AGENT else ""
        print(f"  {name:12s} — {cfg['desc']}{mark}")


def cmd_tools():
    print("=== Tools ===")
    for t in list_tools():
        perms = ",".join(t["permissions"])
        print(f"  {t['name']:20s} [{perms}] — {t['description']}")


def cmd_skills():
    try:
        from skills.skill_loader import list_skills
        skills = list_skills()
        print(f"=== Skills ({len(skills)}) ===")
        for s in skills:
            print(f"  {s.name:20s} — {s.description}")
    except Exception as e:
        print(f"❌ Не удалось загрузить skills: {e}")


def cmd_report():
    sentinel_dir = os.path.expanduser("~/rumix/logs/sentinel")
    reports = sorted(glob.glob(os.path.join(sentinel_dir, "*.md")))
    if reports:
        print(f"📄 Последний: {reports[-1]}")
    else:
        print("Отчётов пока нет.")


def cmd_model():
    model_file = os.path.expanduser("~/.neon_model")
    if os.path.exists(model_file):
        with open(model_file) as f:
            print(f"🎯 Модель: {f.read().strip()}")
    else:
        print("🎯 Модель: по умолчанию (qwen3-0.6b-q4.gguf)")


def cmd_state():
    print(f"🎯 Agent: {agents_mod.CURRENT_AGENT}")
    cfg = AGENTS[agents_mod.CURRENT_AGENT]
    print(f"🌡  Temperature: {cfg['temperature']}")
    print(f"📏 Max tokens: {cfg['max_tokens']}")


def cmd_help():
    print("""
=== Команды ===
  /agents          — список агентов
  /agent <name>    — переключить
  @<name> <task>   — переключить + выполнить
  /tools           — список tools
  /skills          — список skills
  /report          — путь к последнему отчёту
  /model           — текущая модель
  /state           — состояние
  /help            — справка
  /quit            — выйти

Просто текст → full cycle (Router → Tools → Evidence → Qwen → Report)
""")


def handle_command(text):
    """Обработка команд. Возвращает True, если обработано."""
    if text == "/quit" or text == "/exit":
        return "quit"
    if text == "/agents":
        cmd_agents(); return True
    if text == "/tools":
        cmd_tools(); return True
    if text == "/skills":
        cmd_skills(); return True
    if text == "/report":
        cmd_report(); return True
    if text == "/model":
        cmd_model(); return True
    if text == "/state":
        cmd_state(); return True
    if text == "/help":
        cmd_help(); return True
    if text.startswith("/agent "):
        name = text.split(maxsplit=1)[1].strip()
        if name in AGENTS:
            switch_agent(name)
        else:
            print(f"❌ Неизвестный агент: {name}")
        return True
    return False


def main():
    if not health():
        print("❌ llama-server не отвечает на 127.0.0.1:8080")
        print("   Запусти: neon start")
        sys.exit(1)

    print("🤖 Agent Runtime v2. Full cycle.")
    print(f"🎯 Текущий: {agents_mod.CURRENT_AGENT}")
    print("📋 /help — справка.")
    print("")

    while True:
        try:
            text = input(f"[{agents_mod.CURRENT_AGENT}] > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 До встречи.")
            break

        if not text:
            continue

        # Команды
        result = handle_command(text)
        if result == "quit":
            print("👋 До встречи.")
            break
        if result:
            continue

        # @agent inline
        name, task = parse_inline(text)
        if name:
            if name in AGENTS:
                switch_agent(name)
            else:
                print(f"❌ Неизвестный агент: {name}")
                continue

        if not task:
            continue

        # Full cycle через orchestrator
        try:
            answer, evidence, latency, baseline = run_agent_with_tools(
                agents_mod.CURRENT_AGENT, task, max_tokens=400
            )
            print("")
            print("=== ОТВЕТ ===")
            print(answer)
            print("")
            print("=== LATENCY ===")
            for k, v in latency.items():
                print(f"  {k}: {v}s")
        except Exception as e:
            print(f"❌ Ошибка: {e}")

        print("")


if __name__ == "__main__":
    main()
