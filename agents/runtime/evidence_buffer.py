#!/data/data/com.termux/files/usr/bin/env python3
"""
evidence_buffer.py — Evidence Buffer v0.1.

Память о фактах. Только хранит. Не валидирует.

Поля Evidence (по карте v3, раздел 18.4):
- source       — откуда (tool name)
- timestamp    — когда
- test         — что проверяли
- result       — что получили
- status       — full / partial / unavailable / error
- confidence   — high / medium / low
- limitations  — чего не видели
- raw_ref      — ссылка на сырой вывод
- conflict     — bool (противоречие)

Хранилище: ~/rumix/agents/evidence.jsonl — append-only.
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, List


STORAGE = Path.home() / "rumix" / "agents" / "evidence.jsonl"


@dataclass
class Evidence:
    """Типизированное Evidence. Соответствует 9 полям карты v3."""
    source: str
    test: str
    result: str
    schema_version: int = 1
    timestamp: str = ""
    status: str = "full"          # full / partial / unavailable / error
    confidence: str = "medium"    # high / medium / low
    limitations: List[str] = field(default_factory=list)
    raw_ref: Optional[str] = None
    conflict: bool = False

    def to_dict(self):
        return asdict(self)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class EvidenceBuffer:
    def __init__(self, storage=None):
        self.storage = Path(storage) if storage else STORAGE
        self.storage.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage.exists():
            self.storage.touch()

    def record(self, source, test, result,
               status="full", confidence="medium",
               limitations=None, raw_ref=None, conflict=False,
               timestamp=None):
        """Записать Evidence. Append-only. Типизация через dataclass."""
        ev = Evidence(
            source=source,
            test=test,
            result=result,
            status=status,
            confidence=confidence,
            limitations=limitations or [],
            raw_ref=raw_ref,
            conflict=conflict,
            timestamp=timestamp or "",
        )
        ev_dict = ev.to_dict()
        with open(self.storage, "a", encoding="utf-8") as f:
            f.write(json.dumps(ev_dict, ensure_ascii=False) + "\n")
        return ev_dict

    def get_all(self):
        """Все Evidence."""
        if not self.storage.exists():
            return []
        out = []
        with open(self.storage, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        out.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        return out

    def get_by_source(self, source):
        """Evidence по источнику."""
        return [e for e in self.get_all() if e.get("source") == source]

    def count(self):
        return len(self.get_all())

    def clear(self):
        """Очистить buffer. Осторожно."""
        self.storage.write_text("", encoding="utf-8")


if __name__ == "__main__":
    buf = EvidenceBuffer()
    print(f"Evidence Buffer v0.1")
    print(f"Storage: {buf.storage}")
    print(f"Записей: {buf.count()}")
