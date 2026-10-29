"""
maigret.py — обёртка над Maigret (поиск по нику).
"""
import subprocess
import json
import os


def search_username(username: str, timeout: int = 30, no_recursion: bool = True, no_extracting: bool = True, top_sites: int = 0) -> dict:
    """Ищет ник в соцсетях через Maigret. Возвращает dict с результатами."""
    cmd = [
        "maigret", username,
        "--json", "simple",
        "--timeout", str(timeout),
    ]
    if no_recursion:
        cmd.append("--no-recursion")
    if no_extracting:
        cmd.append("--no-extracting")
    if top_sites > 0:
        cmd.extend(["--top-sites", str(top_sites)])
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 30)
        # maigret пишет JSON в файл, а не в stdout. Ищем файл.
        json_file = f"reports/report_{username}_simple.json"
        if os.path.exists(json_file):
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            os.remove(json_file)
            return {"ok": True, "data": data}
        # Если файла нет — пробуем распарсить stdout
        return {"ok": False, "error": "JSON не найден", "stdout": r.stdout[:500]}
    except Exception as e:
        return {"ok": False, "error": str(e)}


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 core/maigret.py <username>")
        sys.exit(1)
    print(json.dumps(search_username(sys.argv[1]), ensure_ascii=False, indent=2))
