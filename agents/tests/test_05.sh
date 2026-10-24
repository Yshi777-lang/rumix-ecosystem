#!/data/data/com.termux/files/usr/bin/bash
# test_05 — Evidence Buffer: record + count + get_by_source

cd "$HOME/rumix/agents/runtime" || exit 1

python3 -c "
import sys
sys.path.insert(0, '.')
from evidence_buffer import EvidenceBuffer
from pathlib import Path

# Временный storage
tmp = Path.home() / 'rumix' / 'agents' / 'evidence_test.jsonl'
if tmp.exists():
    tmp.unlink()

buf = EvidenceBuffer(storage=tmp)

# Записи
buf.record(source='test_tool', test='t1', result='r1', status='full')
buf.record(source='test_tool', test='t2', result='r2', status='partial')
buf.record(source='other', test='t3', result='r3', status='full')

# Проверки
if buf.count() != 3:
    print('FAIL: count != 3, got', buf.count())
    sys.exit(1)

if len(buf.get_by_source('test_tool')) != 2:
    print('FAIL: get_by_source(test_tool) != 2')
    sys.exit(1)

last = buf.get_all()[-1]
if last.get('source') != 'other':
    print('FAIL: last source != other')
    sys.exit(1)

# Убираем временный storage
tmp.unlink()

print('OK: Evidence Buffer записывает и фильтрует')
sys.exit(0)
"
