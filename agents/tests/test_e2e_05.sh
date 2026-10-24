#!/data/data/com.termux/files/usr/bin/bash
# TEST-E2E-05 — Некорректный ответ не становится подтверждённым фактом.
# Проверяет: Evidence Validator отклоняет Claim без Evidence.

cd "$HOME/rumix/agents/runtime" || exit 1

python3 -c "
import sys; sys.path.insert(0, '.')
from evidence_validator import EvidenceValidator, Claim, Verdict

v = EvidenceValidator()

# Claim без Evidence — NO_EVIDENCE
r = v.validate(
    Claim('tool', 'status', 'AVAILABLE'),
    [],  # пустой Evidence
)

if r['verdict'] != Verdict.NO_EVIDENCE:
    print('FAIL: ожидали NO_EVIDENCE, получили:', r['verdict'])
    sys.exit(1)

# Claim, который противоречит Evidence — UNSUPPORTED
r = v.validate(
    Claim('netlink', 'status', 'AVAILABLE'),
    [{'source': 'netlink', 'status': 'UNAVAILABLE'}],
)

if r['verdict'] != Verdict.UNSUPPORTED:
    print('FAIL: ожидали UNSUPPORTED, получили:', r['verdict'])
    sys.exit(1)

# CONFLICT — два источника противоречат
r = v.validate(
    Claim('tool', 'status', 'AVAILABLE'),
    [
        {'source': 'tool', 'status': 'AVAILABLE'},
        {'source': 'tool', 'status': 'UNAVAILABLE'},
    ],
)

if r['verdict'] != Verdict.CONFLICT:
    print('FAIL: ожидали CONFLICT, получили:', r['verdict'])
    sys.exit(1)

print('OK: некорректный ответ не становится подтверждённым фактом')
sys.exit(0)
"
