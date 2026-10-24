#!/data/data/com.termux/files/usr/bin/env python3
"""
evidence_validator.py — Evidence Validator v0.1.

Проверяет, соответствует ли Claim имеющимся Evidence.
Не создаёт правил. Не разрешает конфликты.
Детерминированный. Без NLP.

Разделение:
- Tool       -> наблюдает
- Buffer     -> хранит
- Validator  -> проверяет  <- это
- Agent      -> интерпретирует
- Qwen       -> формулирует

Исходы:
- SUPPORTED    — Claim подтверждён
- UNSUPPORTED  — Claim не подтверждён
- CONFLICT     — два Evidence противоречат
- NO_EVIDENCE  — нет Evidence для проверки
"""

import json
from pathlib import Path


class Verdict:
    SUPPORTED = "SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"
    CONFLICT = "CONFLICT"
    NO_EVIDENCE = "NO_EVIDENCE"


from dataclasses import dataclass


@dataclass
class Claim:
    """Простой Claim: source + field + value."""
    source: str
    field: str
    value: object

    def __repr__(self):
        return f"Claim({self.source}.{self.field} == {self.value!r})"

    def to_dict(self):
        return {"source": self.source, "field": self.field, "value": self.value}


class EvidenceValidator:
    def __init__(self):
        pass

    def _extract(self, evidence, field):
        """Извлечь поле из evidence. Простой доступ по ключу."""
        if not isinstance(evidence, dict):
            return None
        return evidence.get(field)

    def validate(self, claim, evidence_list):
        """
        Проверить Claim против списка Evidence.

        Возвращает dict:
          verdict: SUPPORTED / UNSUPPORTED / CONFLICT / NO_EVIDENCE
          matches: сколько evidence совпало
          conflicts: сколько противоречит
          reason: краткое объяснение
        """
        # Фильтр Evidence по source Claim
        relevant = [e for e in evidence_list if e.get("source") == claim.source]

        if not relevant:
            return {
                "verdict": Verdict.NO_EVIDENCE,
                "matches": 0,
                "conflicts": 0,
                "reason": f"Нет Evidence от source={claim.source}",
                "claim": claim.to_dict(),
            }

        matches = []
        conflicts = []

        for ev in relevant:
            value = self._extract(ev, claim.field)
            if value is None:
                # Поля нет — не считаем ни за, ни против
                continue
            if value == claim.value:
                matches.append(ev)
            else:
                conflicts.append(ev)

        # CONFLICT: есть и совпадения, и противоречия
        if matches and conflicts:
            return {
                "verdict": Verdict.CONFLICT,
                "matches": len(matches),
                "conflicts": len(conflicts),
                "reason": f"Есть и совпадения ({len(matches)}), и противоречия ({len(conflicts)})",
                "claim": claim.to_dict(),
            }

        # SUPPORTED: только совпадения
        if matches and not conflicts:
            return {
                "verdict": Verdict.SUPPORTED,
                "matches": len(matches),
                "conflicts": 0,
                "reason": f"Claim подтверждён {len(matches)} Evidence",
                "claim": claim.to_dict(),
            }

        # UNSUPPORTED: только противоречия
        if conflicts and not matches:
            return {
                "verdict": Verdict.UNSUPPORTED,
                "matches": 0,
                "conflicts": len(conflicts),
                "reason": f"Claim противоречит {len(conflicts)} Evidence",
                "claim": claim.to_dict(),
            }

        # Ни matches, ни conflicts (поля нет в Evidence)
        return {
            "verdict": Verdict.NO_EVIDENCE,
            "matches": 0,
            "conflicts": 0,
            "reason": f"Поле '{claim.field}' отсутствует в Evidence",
            "claim": claim.to_dict(),
        }


if __name__ == "__main__":
    v = EvidenceValidator()
    print("Evidence Validator v0.1")
    print("Задача: проверить Claim против Evidence.")
    print("Исходы: SUPPORTED / UNSUPPORTED / CONFLICT / NO_EVIDENCE.")
