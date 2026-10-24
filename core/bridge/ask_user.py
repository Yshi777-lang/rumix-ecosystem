"""
ask_user.py — умный запрос к пользователю (как AskUserTool из WebToApp).
Поддерживает варианты, рекомендации, multi-select.
"""

from typing import List, Dict, Optional


class AskUser:
    """Запрос с вариантами. В CLI — текстовый, в Shell — кнопки."""

    @staticmethod
    def ask(question: str, options: List[Dict], multi: bool = False, default: Optional[str] = None) -> List[str]:
        """
        Задать вопрос с вариантами.
        options: [{"label": "...", "value": "...", "recommended": bool}]
        Возвращает список выбранных value.
        """
        print(f"\n❓ {question}")
        for i, opt in enumerate(options, 1):
            mark = " (рекомендуется)" if opt.get("recommended") else ""
            print(f"  {i}) {opt['label']}{mark}")
        if multi:
            print("  (можно несколько через запятую)")
        if default:
            print(f"  Enter — по умолчанию: {default}")

        try:
            raw = input("Выбор: ").strip()
        except (EOFError, KeyboardInterrupt):
            return [default] if default else []

        if not raw and default:
            return [default]

        if multi:
            parts = [p.strip() for p in raw.split(",") if p.strip()]
        else:
            parts = [raw]

        chosen = []
        for p in parts:
            if p.isdigit() and 1 <= int(p) <= len(options):
                chosen.append(options[int(p) - 1]["value"])
            elif any(opt["value"] == p for opt in options):
                chosen.append(p)

        return chosen

    @staticmethod
    def confirm(question: str, default: bool = False) -> bool:
        """Простое подтверждение (y/N)."""
        suffix = "Y/n" if default else "y/N"
        try:
            raw = input(f"{question} ({suffix}): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            return default
        if not raw:
            return default
        return raw in ("y", "yes", "д", "да")
