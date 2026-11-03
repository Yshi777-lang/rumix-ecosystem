#!/data/data/com.termux/files/usr/bin/bash
# test_06 — Evidence Validator: SUPPORTED / UNSUPPORTED / NO_EVIDENCE / CONFLICT

cd "$HOME/rumix/agents/runtime" || exit 1

python3 -c "
import sys
sys.path.insert(0, '.')
from evidence_validator import EvidenceValidator, Claim, Verdict

v = EvidenceValidator()

# SUPPORTED
r = v.validate(
    Claim('ifconfig', 'status', 'AVAILABLE'),
    [{'source': 'ifconfig', 'status': 'AVAILABLE'}],
)
if r['verdict'] != Verdict.SUPPORTED:
    print('FAIL 01: ожидали SUPPORTED, получили', r['verdict'])
    sys.exit(1)

# UNSUPPORTED
r = v.validate(
    Claim('netlink', 'status', 'AVAILABLE'),
    [{'source': 'netlink', 'status': 'UNAVAILABLE'}],
)
if r['verdict'] != Verdict.UNSUPPORTED:
    print('FAIL 02: ожидали UNSUPPORTED, получили', r['verdict'])
    sys.exit(1)

# NO_EVIDENCE
r = v.validate(Claim('unknown', 'status', 'AVAILABLE'), [])
if r['verdict'] != Verdict.NO_EVIDENCE:
    print('FAIL 03: ожидали NO_EVIDENCE, получили', r['verdict'])
    sys.exit(1)

# CONFLICT
r = v.validate(
    Claim('tool', 'status', 'AVAILABLE'),
    [
        {'source': 'tool', 'status': 'AVAILABLE'},
        {'source': 'tool', 'status': 'UNAVAILABLE'},
    ],
)
if r['verdict'] != Verdict.CONFLICT:
    print('FAIL 04: ожидали CONFLICT, получили', r['verdict'])
    sys.exit(1)

print('OK: Validator — 4 исхода работают')
sys.exit(0)
"
