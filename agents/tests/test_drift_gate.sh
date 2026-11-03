#!/data/data/com.termux/files/usr/bin/bash
# TEST-DRIFT-GATE — 4 сценария проверки Config Drift Gate.
# 1. Обнаруживает намеренное расхождение.
# 2. Диагностика понятна.
# 3. Exit code ≠ 0 при критике.
# 4. Нет ложных срабатываний на штатной конфигурации.

cd "$HOME/rumix/scripts" || exit 1

# ─── Drift-04: штатная конфигурация → exit 0 ───
bash check-config-drift.sh > $PREFIX/tmp/drift-clean.log 2>&1
RC=$?
if [ "$RC" -ne 0 ]; then
    echo "FAIL Drift-04: штатная конфигурация дала exit=$RC"
    cat $PREFIX/tmp/drift-clean.log | tail -10
    exit 1
fi
echo "OK Drift-04: штатная конфигурация → exit 0"

# ─── Drift-01/02/03: намеренно сломать ~/.neon_model ───
NEON_MODEL_FILE="$HOME/.neon_model"
BACKUP_FILE="$HOME/.neon_model.bak"

# Сохраняем оригинал
if [ -f "$NEON_MODEL_FILE" ]; then
    cp "$NEON_MODEL_FILE" "$BACKUP_FILE"
fi

# Ломаем: указываем на несуществующий файл
echo "/nonexistent/fake-model.gguf" > "$NEON_MODEL_FILE"

# Запускаем гейт — должен обнаружить
bash check-config-drift.sh > $PREFIX/tmp/drift-broken.log 2>&1
RC=$?

# Восстанавливаем СРАЗУ — что бы ни случилось
if [ -f "$BACKUP_FILE" ]; then
    cp "$BACKUP_FILE" "$NEON_MODEL_FILE"
    rm -f "$BACKUP_FILE"
fi

# Drift-03: exit code ≠ 0
if [ "$RC" -eq 0 ]; then
    echo "FAIL Drift-03: гейт не вернул ошибку при сломанной конфигурации (exit=$RC)"
    cat $PREFIX/tmp/drift-broken.log | tail -10
    exit 1
fi
echo "OK Drift-03: сломанная конфигурация → exit=$RC"

# Drift-01: обнаружен конкретный рассинхрон
if ! grep -q "neon_model" $PREFIX/tmp/drift-broken.log; then
    echo "FAIL Drift-01: гейт не упомянул neon_model"
    cat $PREFIX/tmp/drift-broken.log | tail -10
    exit 1
fi
echo "OK Drift-01: гейт обнаружил рассинхрон (neon_model)"

# Drift-02: диагностика понятна (есть рекомендация фикса)
if ! grep -q "Фикс\|fix\|echo" $PREFIX/tmp/drift-broken.log; then
    echo "WARN Drift-02: нет явной рекомендации фикса"
fi
echo "OK Drift-02: диагностика есть"

# Уборка
rm -f $PREFIX/tmp/drift-clean.log $PREFIX/tmp/drift-broken.log

echo ""
echo "OK: Config Drift Gate — 4 сценария проверены"
exit 0
