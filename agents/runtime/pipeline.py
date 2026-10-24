#!/data/data/com.termux/files/usr/bin/env python3
"""
pipeline.py — цепочка агентов.

TASK → ARCHITECT → CODER → REVIEWER → RESULT

С урезанными outputs между агентами (для 0.6B).
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from runtime.local_provider import LocalProvider
from runtime.provider import ModelRequest
from runtime.context import build_messages
from runtime.agents import AGENTS


def run_agent(name, task, max_out=None):
    """Запуск одного агента."""
    cfg = AGENTS[name]
    messages = build_messages(name, task)
    max_tokens = max_out or cfg["max_tokens"]

    provider = LocalProvider()
    req = ModelRequest(
        messages=messages,
        temperature=cfg["temperature"],
        max_tokens=max_tokens,
    )
    resp = provider.generate(req)
    return resp.text


def pipeline(task, verbose=True):
    """architect → neon → reviewer."""
    if verbose:
        print("=" * 60)
        print(f"🔄 PIPELINE: {task[:60]}...")
        print("=" * 60)

    # 1. Architect
    if verbose:
        print("\n[1/3] 🏛  Architect думает...")
    plan = run_agent("architect", task, max_out=400)
    plan = plan[:600]
    if verbose:
        print(f"\n{plan}\n")

    # 2. Neon — код
    if verbose:
        print("[2/3] 🤖 Neon пишет код...")
    code_task = (
        f"TASK:\n{task}\n\n"
        f"PLAN:\n{plan}\n\n"
        f"Реализуй. Только код + минимум пояснений."
    )
    code = run_agent("neon", code_task, max_out=800)
    code = code[:1500]
    if verbose:
        print(f"\n{code}\n")

    # 3. Reviewer
    if verbose:
        print("[3/3] 🔍 Reviewer проверяет...")
    review_task = (
        f"TASK:\n{task}\n\n"
        f"CODE:\n{code}\n\n"
        f"Проверь. Коротко: BUGS / RISKS / FIX."
    )
    review = run_agent("reviewer", review_task, max_out=400)
    review = review[:600]
    if verbose:
        print(f"\n{review}\n")

    return {
        "task": task,
        "plan": plan,
        "code": code,
        "review": review,
    }


if __name__ == "__main__":
    task = "Напиши bash-скрипт backup.sh, который создаёт архив папки ~/Work в ~/backups/"
    result = pipeline(task)

    print("=" * 60)
    print("✅ PIPELINE завершён")
    print(f"📋 Plan: {len(result['plan'])} chars")
    print(f"💻 Code: {len(result['code'])} chars")
    print(f"🔍 Review: {len(result['review'])} chars")
