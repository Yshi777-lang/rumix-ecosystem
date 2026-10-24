#!/data/data/com.termux/files/usr/bin/env python3
"""
skill_loader.py — загрузчик skills.

Читает SKILL.md (YAML frontmatter + markdown).
Парсит: name, description, tools, output, keywords.
Выбирает skills по задаче (роутер).
"""

import os
import re
from pathlib import Path


class Skill:
    def __init__(self, name, description, tools, output, body, path, keywords=None):
        self.name = name
        self.description = description
        self.tools = tools
        self.output = output
        self.body = body
        self.path = path
        self.keywords = keywords or []

    def matches(self, task):
        """Проверить, подходит ли skill к задаче."""
        t = task.lower()
        for kw in self.keywords:
            if kw.lower() in t:
                return True
        return False

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "tools": self.tools,
            "output": self.output,
            "keywords": self.keywords,
            "path": str(self.path),
        }


def parse_frontmatter(text):
    """Парсит YAML frontmatter."""
    if not text.startswith("---"):
        return {}, text

    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text

    fm_text = parts[1].strip()
    body = parts[2].strip()

    result = {}
    current_key = None
    current_list = None

    for line in fm_text.splitlines():
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
                result[key] = value
                current_key = None
                current_list = None
            else:
                result[key] = []
                current_key = key
                current_list = result[key]
        elif stripped.endswith(":"):
            key = stripped[:-1].strip()
            result[key] = []
            current_key = key
            current_list = result[key]

    return result, body


def parse_skill(path):
    """Загрузить один skill."""
    path = Path(path)
    if not path.exists():
        return None

    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    fm, body = parse_frontmatter(text)

    name = fm.get("name", path.parent.name)
    description = fm.get("description", "")
    tools = fm.get("tools", [])
    output = fm.get("output", [])
    keywords = fm.get("keywords", [])

    if isinstance(tools, str):
        tools = [tools]
    if isinstance(output, str):
        output = [output]
    if isinstance(keywords, str):
        keywords = [keywords]

    return Skill(name, description, tools, output, body, path, keywords)


def list_skills(skills_dir=None):
    """Список всех skills."""
    if skills_dir is None:
        skills_dir = Path(__file__).parent
    skills_dir = Path(skills_dir)

    skills = []
    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if skill_md.exists():
            s = parse_skill(skill_md)
            if s:
                skills.append(s)
    return skills


def pick_skills(task, skills=None):
    """Выбрать skills, подходящие к задаче."""
    if skills is None:
        skills = list_skills()
    return [s for s in skills if s.matches(task)]


if __name__ == "__main__":
    print("=== Все skills ===")
    for s in list_skills():
        print(f"  {s.name}: {s.description}")
        print(f"    keywords: {s.keywords}")

    print()
    print("=== pick_skills('аудит безопасности') ===")
    for s in pick_skills("аудит безопасности"):
        print(f"  {s.name}")

    print()
    print("=== pick_skills('проверь сеть и DNS') ===")
    for s in pick_skills("проверь сеть и dns"):
        print(f"  {s.name}")
