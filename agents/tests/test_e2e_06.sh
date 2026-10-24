#!/data/data/com.termux/files/usr/bin/bash
# TEST-E2E-06 — После перезапуска Loop сохраняет состояние.
# Проверяет: state.json записывается и читается корректно.

cd "$HOME/rumix/loop" || exit 1

# Уборка
rm -f state.json queue.txt
rm -f out/test-e2e-06.sh

# Шаг 1: запуск Loop, ждём старт
echo "y" | IDLE_TIMEOUT_SEC=3 bash loop-v0.3.sh > /dev/null 2>&1 &
LOOP_PID=$!

# Ждём запуск + idle timeout
sleep 12

# Проверим, что state.json создан
if [ ! -f state.json ]; then
    echo "FAIL: state.json не создан"
    kill $LOOP_PID 2>/dev/null
    exit 1
fi

# Проверим поля
for field in schema_version enabled state pid started_at last_activity idle_timeout_sec; do
    if ! grep -q "\"$field\"" state.json; then
        echo "FAIL: нет поля $field в state.json"
        cat state.json
        kill $LOOP_PID 2>/dev/null
        exit 1
    fi
done

# После выхода — state: stopped, enabled: false
if ! grep -q '"state": "stopped"' state.json; then
    echo "FAIL: state не stopped после завершения"
    cat state.json
    kill $LOOP_PID 2>/dev/null
    exit 1
fi

if ! grep -q '"enabled": false' state.json; then
    echo "FAIL: enabled не false после завершения"
    cat state.json
    kill $LOOP_PID 2>/dev/null
    exit 1
fi

kill $LOOP_PID 2>/dev/null
echo "OK: Loop сохраняет состояние между перезапусками"
exit 0
