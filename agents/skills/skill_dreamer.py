#!/data/data/com.termux/files/usr/bin/env python3
"""
skill_dreamer.py — AI генерирует новый SKILL.md.

Аналог PluginDreamDialog из Termux Ultra.
Пользователь: "Хочу skill для X".
AI: генерирует SKILL.md.
Система: валидирует и сохраняет.
"""

import os
import re
import sys
from pathlib import Path

# Добавляем runtime в path
sys.path.insert(0, "/data/data/com.termux/files/home/rumix/agents")

try:
    from runtime.local_provider import LocalProvider
    from runtime.provider import ModelRequest
    provider = LocalProvider()
except ImportError:
    provider = None


SKILL_SPEC_PROMPT = """Ты — генератор skills для дома Rumix.

Пользователь описывает потребность. Ты создаёшь SKILL.md.

Формат SKILL.md:
---
name: <имя-skill (латиница, дефисы)>
description: <краткое описание на русском>
tools:
  - <tool_name>
keywords:
  - <ключевое_слово_1>
  - <ключевое_слово_2>
output:
  - RISKS
  - FINDINGS
  - RECOMMENDATIONS
---

# <Имя Skill>

<Описание>

## Когда применять
<когда использовать>

## Шаги
1. <шаг>
2. <шаг>

## Output
Строго: RISKS / FINDINGS / RECOMMENDATIONS.

Доступные tools:
- system_info, package_info, network_status, read_logs, dns_lookup, run_command.

Ограничения:
- name — латиница, дефисы (^[a-z][a-z0-9-]*$).
- description — не пустая.
- tools — из списка выше.
- keywords — минимум 3, на русском и английском.
- Output — строго RISKS / FINDINGS / RECOMMENDATIONS.

Ответ: ТОЛЬКО SKILL.md, начинай ответ с "---" (три дефиса), заканчивай frontmatter тоже "---".
Без объяснений. Без markdown-обёрток. Пример первого символа ответа: "-".

ВАЖНО:
- name — ТОЛЬКО латиница и дефисы (например: backup-check).
- НЕ используй русские буквы в name.

Формат ответа:
---
name: backup-check
description: Проверка бэкапов
tools:
  - run_command
keywords:
  - backup
  - git
  - бэкап
output:
  - RISKS
  - FINDINGS
  - RECOMMENDATIONS
---

# Backup Check
...
"""


def extract_skill_md(raw):
    """Извлечь SKILL.md из ответа модели."""
    if not raw:
        return None
    # Убрать markdown-обёртки
    fence = re.search(r"```(?:markdown|md)?\s*(.*?)```", raw, re.DOTALL)
    candidate = fence.group(1).strip() if fence else raw.strip()

    # Если есть frontmatter — вернуть как есть
    if candidate.startswith("---"):
        return candidate

    # Fallback: модель забыла ---. Пробуем извлечь frontmatter по ключам
    lines = candidate.splitlines()
    fm_lines = []
    body_lines = []
    in_fm = False
    body_started = False

    for line in lines:
        stripped = line.strip()
        # Начало frontmatter — строка с name:
        if not in_fm and not body_started and stripped.startswith("name:"):
            in_fm = True
        # Конец frontmatter — пустая строка после keywords или начало RISKS
        if in_fm:
            if stripped.startswith("RISKS") or stripped.startswith("## ") or (not stripped and len(fm_lines) > 3):
                in_fm = False
                body_started = True
                if stripped:
                    body_lines.append(line)
            else:
                fm_lines.append(line)
        else:
            body_lines.append(line)

    if not fm_lines:
        return None

    # Собираем: --- + fm + --- + body
    return "---\n" + "\n".join(fm_lines) + "\n---\n\n" + "\n".join(body_lines)


def parse_skill_md(text):
    """Парсит frontmatter и проверяет обязательные поля."""
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    fm = parts[1].strip()
    body = parts[2].strip()

    fields = {}
    current_key = None
    current_list = None

    for line in fm.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("- "):
            if current_key and current_list is not None:
                current_list.append(stripped[2:].strip())
            continue
        if ": " in stripped:
            key, value = stripped.split(": ", 1)
            key = key.strip()
            value = value.strip()
            if value:
                fields[key] = value
                current_key = None
                current_list = None
            else:
                fields[key] = []
                current_key = key
                current_list = fields[key]
        elif stripped.endswith(":"):
            key = stripped[:-1].strip()
            fields[key] = []
            current_key = key
            current_list = fields[key]

    # Валидация
    name = fields.get("name")
    if not name:
        return None
    # Транслитерация: русский -> латиница, пробелы -> дефисы
    translit = {
        "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
        "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
        "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
        "ф": "f", "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sch",
        "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
    }
    translited = ""
    for ch in name.lower():
        if ch in translit:
            translited += translit[ch]
        elif ch.isascii() and (ch.isalnum() or ch == "-"):
            translited += ch
        else:
            translited += "-"
    # Убрать лишние дефисы
    translited = re.sub(r"-+", "-", translited).strip("-")
    if not translited or not re.match(r"^[a-z][a-z0-9-]*$", translited):
        return None
    name = translited
    fields["name"] = name

    description = fields.get("description")
    if not description:
        return None

    tools = fields.get("tools", [])
    if isinstance(tools, str):
        tools = [tools]
    allowed_tools = {"system_info", "package_info", "network_status", "read_logs", "dns_lookup", "run_command"}
    tools = [t for t in tools if t in allowed_tools]
    if not tools:
        return None

    keywords = fields.get("keywords", [])
    if isinstance(keywords, str):
        keywords = [keywords]
    if len(keywords) < 2:
        return None

    output = fields.get("output", [])
    if isinstance(output, str):
        output = [output]
    if not output:
        output = ["RISKS", "FINDINGS", "RECOMMENDATIONS"]

    if not body:
        body = f"# {name}\n\n{description}\n\n## Output\nСтрого: RISKS / FINDINGS / RECOMMENDATIONS."

    return {
        "name": name,
        "description": description,
        "tools": tools,
        "keywords": keywords,
        "output": output,
        "body": body,
    }


def generate_skill(requirement):
    """Сгенерировать SKILL.md по требованию."""
    if provider is None:
        return {"error": "runtime.provider не доступен"}

    messages = [
        {"role": "system", "content": SKILL_SPEC_PROMPT},
        {"role": "user", "content": f"Потребность: {requirement}"},
    ]

    req = ModelRequest(messages=messages, max_tokens=1500, timeout=600)
    resp = provider.generate(req)
    raw = resp.text
    if not raw:
        return {"error": "пустой ответ модели"}

    skill_md = extract_skill_md(raw)
    if not skill_md:
        return {"error": "не найден SKILL.md в ответе", "raw": raw[:500]}

    parsed = parse_skill_md(skill_md)
    if not parsed:
        return {"error": "неверный формат SKILL.md", "raw": skill_md[:500]}

    parsed["raw"] = skill_md
    return parsed


def install_skill(parsed):
    """Сохранить сгенерированный SKILL.md."""
    name = parsed["name"]
    skills_dir = Path("/data/data/com.termux/files/home/rumix/agents/skills")
    skill_dir = skills_dir / name
    if skill_dir.exists():
        return {"error": f"skill уже существует: {name}"}

    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_path = skill_dir / "SKILL.md"
    with open(skill_path, "w", encoding="utf-8") as f:
        f.write(parsed["raw"])

    return {"ok": True, "path": str(skill_path)}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python3 skill_dreamer.py 'требование'")
        sys.exit(1)

    req = " ".join(sys.argv[1:])
    print(f"Требование: {req}")
    print("Генерирую SKILL.md...")

    result = generate_skill(req)
    if "error" in result:
        print(f"❌ {result['error']}")
        if "raw" in result:
            print("--- RAW ---")
            print(result["raw"])
        sys.exit(1)

    print(f"✅ Сгенерирован: {result['name']}")
    print(f"   description: {result['description']}")
    print(f"   tools: {result['tools']}")
    print(f"   keywords: {result['keywords']}")

    install = install_skill(result)
    if "error" in install:
        print(f"❌ {install['error']}")
        sys.exit(1)

    print(f"📄 Сохранён: {install['path']}")
