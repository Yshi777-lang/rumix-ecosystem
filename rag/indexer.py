import os
import json
from pathlib import Path

WORK_DIR = Path.home() / "Work"
SCORE_FILE = Path.home() / "rumix" / "rag" / "scores.json"

def scan_md():
    scores = {}
    for md in WORK_DIR.rglob("*.md"):
        try:
            text = md.read_text(encoding="utf-8")
            score = len(text)
            scores[str(md)] = score
        except:
            pass
    SCORE_FILE.write_text(json.dumps(scores, indent=2, ensure_ascii=False))
    print(f"Просканировано {len(scores)} файлов.")

if __name__ == "__main__":
    scan_md()
