#!/data/data/com.termux/files/usr/bin/env python3
"""
orchestrator.py — Router, Tools, Sanitizer, Evidence, Agent.
4 слоя: Tool -> Evidence -> Agent -> Runtime.
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from runtime.local_provider import LocalProvider
from runtime.provider import ModelRequest
from runtime.context import build_messages
from runtime.agents import AGENTS
from runtime.tools import call_tool, format_result
from runtime.sanitizer import sanitize_dict
from runtime.fake_output import detect_fake_output
import sys as _sys
_sys.path.insert(0, '/data/data/com.termux/files/home/rumix/agents')
from skills.skill_loader import list_skills, pick_skills


TOOL_ROUTES = [
    ("аудит",    ["system_info", "package_info", "network_status", "dns_lookup", "read_logs"]),
    ("audit",    ["system_info", "package_info", "network_status", "dns_lookup", "read_logs"]),
    ("безопас",  ["system_info", "package_info", "network_status", "dns_lookup", "read_logs"]),
    ("security", ["system_info", "package_info", "network_status", "dns_lookup", "read_logs"]),
    ("систем",   ["system_info", "package_info"]),
    ("system",   ["system_info", "package_info"]),
    ("сеть",     ["network_status", "dns_lookup"]),
    ("network",  ["network_status", "dns_lookup"]),
    ("dns",      ["dns_lookup"]),
    ("лог",      ["read_logs"]),
    ("log",      ["read_logs"]),
]


def pick_tools(task):
    """Определить, какие tools нужны для задачи."""
    t = task.lower()
    for key, tools in TOOL_ROUTES:
        if key in t:
            return tools
    return []


TOOL_ARGS = {
    "dns_lookup": {"domain": "example.com"},
    "read_logs": {"path": None, "lines": 5},
}


def call_tool_with_args(tool_name, auto_approve=True):
    args = TOOL_ARGS.get(tool_name, {})
    return call_tool(tool_name, auto_approve=auto_approve, **args)


def verification_summary(evidence_set, latency_report):
    """Verification cards: список проверок после turn."""
    if not evidence_set:
        return []
    cards = []
    for name, ev in evidence_set.items():
        data = ev.get("data", {})
        confidence = ev.get("confidence", "medium")
        latency = latency_report.get(name, 0)

        if not data:
            status = "unconfirmed"
        elif isinstance(data, dict) and "error" in data:
            status = "failed"
        elif isinstance(data, dict) and data.get("status") == "partial":
            status = "partial"
        else:
            status = "passed"

        cards.append({
            "source": name,
            "status": status,
            "confidence": confidence,
            "latency_s": latency,
        })
    return cards


def format_verification(cards):
    """Красивый вывод verification cards."""
    if not cards:
        return ""
    lines = ["", "=== VERIFICATION ==="]
    for c in cards:
        icon = {"passed": "✅", "failed": "❌", "partial": "⚠️", "unconfirmed": "➖"}.get(c["status"], "?")
        lines.append(f"  {icon} [{c['source']}] {c['status']} ({c['confidence']}, {c['latency_s']}s)")
    return "\n".join(lines)


def run_agent_with_tools(agent_name, task, max_tokens=None):
    """Запуск агента с автоматическим вызовом tools.
    Возвращает: (ответ, evidence_set, latency_report, baseline)."""
    if agent_name not in AGENTS:
        raise ValueError(f"Unknown agent: {agent_name}")

    cfg = AGENTS[agent_name]

    # 1. Router
    tool_names = pick_tools(task)
    print(f"Router: tools -> {tool_names or 'нет'}")

    # 2. Tools + Sanitizer + Evidence + Latency
    evidence_set = {}
    latency_report = {}
    for tool_name in tool_names:
        print(f"   вызов {tool_name}()...")
        t0 = time.time()
        raw = call_tool_with_args(tool_name, auto_approve=True)
        elapsed = time.time() - t0
        latency_report[tool_name] = round(elapsed, 3)
        print(f"      [{tool_name}] {elapsed:.2f}s")

        clean = sanitize_dict(raw)

        is_error = isinstance(clean, dict) and "error" in clean
        evidence_set[tool_name] = {
            "source": tool_name,
            "confidence": "low" if is_error else "medium",
            "data": clean,
        }

    # 3. Задача с evidence
    if evidence_set:
        blocks = []
        for name, ev in evidence_set.items():
            data = format_result(ev["data"])
            blocks.append(f"=== {name} (confidence: {ev['confidence']}) ===\n{data}")
        data_block = "\n\n".join(blocks)

        # Загружаем доступные skills
        skills_block = ""
        try:
            skills = pick_skills(task)
            if not skills:
                # Fallback — все skills
                skills = list_skills()
            if skills:
                skill_lines = []
                for s in skills:
                    skill_lines.append(f"- {s.name}: {s.description}")
                skills_block = "\n\nДоступные skills:\n" + "\n".join(skill_lines)
        except Exception:
            pass

        full_task = (
            f"{task}\n\n"
            f"Собранные данные (Evidence):\n\n{data_block}\n\n"
            f"В отчёте указывай source для каждого FINDING."
            f"{skills_block}"
        )
    else:
        full_task = task

    # 4. Context check
    messages = build_messages(agent_name, full_task)
    total_chars = sum(len(m.get("content", "")) for m in messages)
    approx_tokens = total_chars // 3
    CONTEXT_LIMIT = 8192
    MAX_OUT = max_tokens or cfg["max_tokens"]
    SAFE_LIMIT = CONTEXT_LIMIT - MAX_OUT - 200

    if approx_tokens > SAFE_LIMIT:
        print(f"      Context warning: ~{approx_tokens} > {SAFE_LIMIT}")
    else:
        print(f"      Context: ~{approx_tokens} tokens (limit ~{SAFE_LIMIT})")

    # 5. Qwen
    t0 = time.time()
    provider = LocalProvider()
    req = ModelRequest(
        messages=messages,
        temperature=cfg["temperature"],
        max_tokens=max_tokens or cfg["max_tokens"],
    )
    resp = provider.generate(req)
    qwen_elapsed = time.time() - t0
    latency_report["__qwen__"] = round(qwen_elapsed, 3)

    answer = resp.text
    qwen_usage = resp.usage
    qwen_timings = resp.timings

    # Turn metrics: throughput, tokens
    if qwen_timings:
        latency_report["__qwen_throughput_tps__"] = round(qwen_timings.get("predicted_per_second", 0), 2)
        latency_report["__qwen_prompt_ms__"] = round(qwen_timings.get("prompt_ms", 0), 1)
        latency_report["__qwen_prompt_n__"] = qwen_timings.get("prompt_n", 0)
        latency_report["__qwen_predicted_n__"] = qwen_timings.get("predicted_n", 0)
    if qwen_usage:
        latency_report["__qwen_total_tokens__"] = qwen_usage.get("total_tokens", 0)

    # FAKE OUTPUT CHECK
    fake_check = detect_fake_output(answer)
    if fake_check.is_fake:
        print(f"      [FakeCheck] ⚠️  {len(fake_check.violations)} нарушений")
        for v in fake_check.violations:
            print(f"         - {v}")
    else:
        print(f"      [FakeCheck] ✅ чисто")

    baseline = {
        "latency": latency_report,
        "usage": qwen_usage,
        "timings": qwen_timings,
        "fake_check": fake_check.to_dict(),
    }

    # Verification cards
    cards = verification_summary(evidence_set, latency_report)
    print(format_verification(cards))

    return answer, evidence_set, latency_report, baseline


def save_report(task, evidence, latency, answer):
    """Сохранить отчёт Sentinel в файл."""
    from datetime import datetime
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    reports_dir = os.path.expanduser("~/rumix/logs/sentinel")
    os.makedirs(reports_dir, exist_ok=True)
    path = os.path.join(reports_dir, f"{ts}-sentinel.md")

    lines = []
    lines.append(f"# Sentinel Report — {datetime.now().isoformat()}")
    lines.append("")
    lines.append("## Task")
    lines.append(task)
    lines.append("")
    lines.append("## Tools")
    for name in evidence.keys():
        lines.append(f"- {name}: {latency.get(name, '?')}s")
    lines.append("")
    lines.append(f"## Qwen: {latency.get('__qwen__', '?')}s")
    lines.append("")
    lines.append("## Answer")
    lines.append(answer)
    lines.append("")

    with open(path, "w") as f:
        f.write("\n".join(lines))
    return path


if __name__ == "__main__":
    agent = "sentinel"
    task = "Проведи аудит безопасности системы. Формат: RISKS, FINDINGS, RECOMMENDATIONS. Для каждого FINDING указывай source."

    print("=" * 60)
    print(f"Agent: {agent}")
    print(f"Task: {task}")
    print("=" * 60)
    print("")

    answer, evidence, latency, baseline = run_agent_with_tools(agent, task, max_tokens=500)

    print("")
    print("=== EVIDENCE SET ===")
    for name, ev in evidence.items():
        print(f"  {name}: source={ev['source']} confidence={ev['confidence']}")

    print("")
    print("=== LATENCY ===")
    for k, v in latency.items():
        print(f"  {k}: {v}s")

    print("")
    print("=== ОТВЕТ ===")
    print(answer)

    report_path = save_report(task, evidence, latency, answer)
    print("")
    print(f"📄 Отчёт сохранён: {report_path}")

    import json as _json
    from datetime import datetime as _dt
    baseline_dir = os.path.expanduser("~/rumix/logs/baseline")
    os.makedirs(baseline_dir, exist_ok=True)
    ts = _dt.now().strftime("%Y-%m-%d_%H-%M-%S")
    baseline_path = os.path.join(baseline_dir, f"{ts}-baseline.json")
    baseline["task"] = task
    baseline["agent"] = agent
    baseline["timestamp"] = _dt.now().isoformat()
    with open(baseline_path, "w") as f:
        _json.dump(baseline, f, indent=2, ensure_ascii=False)
    print(f"📊 Baseline сохранён: {baseline_path}")
