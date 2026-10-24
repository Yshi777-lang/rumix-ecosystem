#!/data/data/com.termux/files/usr/bin/env python3
"""
fake_output.py — детектор галлюцинаций (порт detectFakeOutput).
8 запретов. После ответа Qwen.
"""

import re


class FakeCheck:
    def __init__(self, is_fake, violations):
        self.is_fake = is_fake
        self.violations = violations

    def to_dict(self):
        return {"is_fake": self.is_fake, "violations": self.violations}


FAKE_ACTION = [
    r"создал[аи]?\s+(файл|сессию|процесс|каталог)",
    r"создан[аы]?\s+(файл|сессия|процесс|каталог)",
    r"установил[аи]?\s+(пакет|программу|софт)",
    r"подключил(ся|ась)?\s+(SSH|VNC|к\s+удал)",
    r"отправил[аи]?\s+(команд|запрос)",
    r"прочитал[аи]?\s+(файл|каталог)",
    r"записал[аи]?\s+(в\s+файл|данные)",
    r"удалил[аи]?\s+(файл|каталог)",
    r"вывел[аи]?\s+список\s+(файлов|каталогов|сессий|процессов)",
    r"операция\s+успешно\s+(создан|подключен|установлен|записан|удален)",
]

FAKE_INFO = [
    "/proc/", "/data/data/com.termux", "qemu-system",
    "список процессов", "использование памяти", "дисковое пространство",
    "uptime", "load average", "cpu usage",
]

FAKE_OUTPUT = [
    r"\[D\]\s+\S+",
    r"\[F\]\s+\S+",
    r"total\s+\d+",
    r"PID\s+USER\s+COMMAND",
    r"/proc/\d+/status",
    r"MemTotal|MemFree|MemAvailable",
    r"Setting up\s+",
    r"Processing triggers",
]

HOLLOW = [
    "не существует", "нет такого", "не могу выполнить",
    "не поддерживается", "недостаточно прав", "нет доступа",
    "в текущей среде нет", "функция пока", "пока не поддерживается",
    "у меня нет этой функции", "я не могу выполнить",
]

FAKE_SKILLS = [
    "карточка навыка", "умное расписание", "погода", "доставка еды",
    "отслеживание посылки", "голосовой помощник", "перевод", "поиск",
]


def detect_fake_output(content, pre_parsed_skill_count=0):
    """Проверить ответ модели на галлюцинации."""
    violations = []
    if not content:
        return FakeCheck(False, violations)

    lower = content.lower()

    # Проверка skill-блоков
    block_re = re.compile(r"```[a-zA-Z]*\s*\r?\n([\s\S]*?)[\r\n]*```", re.DOTALL)
    inline_re = re.compile(r'\{[^{}]*"skillType"[^{}]*\}', re.DOTALL)

    has_skills = (
        pre_parsed_skill_count > 0
        or bool(block_re.search(content))
        or bool(inline_re.search(content))
    )

    # Запреты 4, 6, 7, 8 — только если нет skill
    if not has_skills:
        for pat in FAKE_ACTION:
            if re.search(pat, lower):
                violations.append(f"[4] Действие без skill: {pat}")
                break

        for pat in HOLLOW:
            if pat in lower:
                violations.append(f"[6] Уверенная пустота: «{pat}»")
                break

        for pat in FAKE_SKILLS:
            if pat in lower and re.search(r"\b(создал|выполнил|активировал|запустил)", lower):
                violations.append(f"[7] Выдуманный skill: «{pat}»")
                break

        if re.search(r"(решение|способ)[\s\S]*?(вы можете|рекомендую|советую)", lower) and len(content) > 200:
            violations.append("[8] Решение вместо выполнения")

    # Запрет 5: фальшивый вывод
    for pat in FAKE_OUTPUT:
        if re.search(pat, content, re.MULTILINE):
            violations.append(f"[5] Фальшивый вывод: {pat}")
            break

    return FakeCheck(bool(violations), violations)


if __name__ == "__main__":
    tests = [
        "echo hi",
        "создал файл /tmp/test.txt",
        "не существует такого файла",
        "total 123\nPID USER COMMAND",
        '```json\n{"skillType": "RUN_COMMAND", "params": {"command": "ls"}}\n```',
    ]
    for t in tests:
        r = detect_fake_output(t)
        status = "⚠️  FAKE" if r.is_fake else "✅ ok"
        print(f"{status}: {t[:50]}  ->  {r.violations[:2]}")
