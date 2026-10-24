#!/data/data/com.termux/files/usr/bin/bash
# check-config-drift.sh — проверка рассинхронов конфигов
# Config Drift Gate. Rumix.
# Идея: check_config_field_drift.py из web-to-app (не наш код).

set -u

issues=0
warnings=0

report_issue() {
    echo "❌ $1"
    issues=$((issues + 1))
}

report_warn() {
    echo "⚠️  $1"
    warnings=$((warnings + 1))
}

echo "🧬 CONFIG DRIFT CHECK"
echo ""

# ─── 1. Пути в скриптах ───
echo "─── Пути ───"

# Все скрипты не должны ссылаться на Work/neon, Work/scripts
bad_paths=$(grep -rn "HOME/Work/neon\|HOME/Work/scripts\|~/Work/neon\|~/Work/scripts" ~/rumix/scripts/*.sh ~/rumix/loop/*.sh 2>/dev/null | grep -v "check-config-drift.sh" || true)
if [ -n "$bad_paths" ]; then
    report_issue "Найдены устаревшие пути Work/neon, Work/scripts:"
    echo "$bad_paths" | head -5 | while read -r line; do echo "      $line"; done
else
    echo "  ✅ Пути в порядке"
fi

# Критичные файлы должны существовать
for f in ~/rumix/neon/character.md ~/rumix/scripts/rumix.sh ~/rumix/loop/loop-v0.3.sh ~/rumix/models/catalog.json; do
    if [ ! -f "$f" ]; then
        report_issue "Файл отсутствует: $f"
    fi
done
echo "  ✅ Критичные файлы на месте"
echo ""

# ─── 2. Модель: catalog.json vs install-neon.sh ───
echo "─── Модель ───"

CATALOG="$HOME/rumix/models/catalog.json"
INSTALL="$HOME/rumix/scripts/install-neon.sh"

if [ -f "$CATALOG" ] && [ -f "$INSTALL" ]; then
    # Извлекаем имя файла модели из каталога
    cat_model=$(python3 -c "
import json, os
c = json.load(open('$CATALOG'))
print(os.path.basename(c['models'][0]['local_path']))
" 2>/dev/null || echo "")

    # Ищем в install-neon.sh упоминание файла
    if [ -n "$cat_model" ]; then
        if grep -q "$cat_model" "$INSTALL"; then
            echo "  ✅ Модель согласована: $cat_model"
        else
            report_warn "install-neon.sh не упоминает модель из каталога: $cat_model"
        fi
    else
        report_warn "Не удалось извлечь модель из catalog.json"
    fi
else
    report_warn "catalog.json или install-neon.sh отсутствует"
fi

# Проверка ~/.neon_model
NEON_MODEL_FILE="$HOME/.neon_model"
if [ -f "$NEON_MODEL_FILE" ]; then
    model_in_file=$(cat "$NEON_MODEL_FILE")
    if [ -f "$model_in_file" ]; then
        echo "  ✅ ~/.neon_model указывает на существующий файл: $(basename "$model_in_file")"
    else
        report_issue "~/.neon_model указывает на несуществующий файл: $model_in_file"
        echo "      Фикс: echo \"\$HOME/models/qwen3-0.6b-q4.gguf\" > ~/.neon_model"
    fi
fi
echo ""

# ─── 3. .zshrc: ключи из setup-rumix.sh ───
echo "─── .zshrc ───"

SETUP="$HOME/rumix/scripts/setup-rumix.sh"
if [ -f "$SETUP" ]; then
    # Проверим, что в шаблоне setup-rumix.sh есть PROMPT_SUBST
    if grep -q "setopt PROMPT_SUBST" "$SETUP"; then
        echo "  ✅ PROMPT_SUBST в шаблоне setup-rumix.sh"
    else
        report_issue "PROMPT_SUBST отсутствует в setup-rumix.sh"
    fi

    # Проверим, что в шаблоне есть termux-services
    if grep -q "start-services.sh" "$SETUP"; then
        echo "  ✅ termux-services в шаблоне setup-rumix.sh"
    else
        report_warn "termux-services отсутствует в setup-rumix.sh"
    fi

    # Проверим, что в шаблоне есть bootstrap
    if grep -q "rumix-setup-done" "$SETUP"; then
        echo "  ✅ bootstrap в шаблоне setup-rumix.sh"
    else
        report_warn "bootstrap отсутствует в setup-rumix.sh"
    fi
else
    report_warn "setup-rumix.sh отсутствует"
fi
echo ""

# ─── 4. Сервис neon (runit) ───
echo "─── Сервис neon ───"

SERVICE_RUN="$PREFIX/var/service/neon/run"
if [ -f "$SERVICE_RUN" ]; then
    # Модель в runite
    if grep -q "qwen3-0.6b" "$SERVICE_RUN"; then
        echo "  ✅ Сервис использует qwen3-0.6b"
    else
        report_warn "Сервис не использует qwen3-0.6b"
    fi

    # Контекст 8192
    if grep -q "\-c 8192" "$SERVICE_RUN"; then
        echo "  ✅ Сервис с -c 8192"
    else
        report_warn "Сервис без -c 8192 (может быть -c 4096)"
    fi

    # Flash Attention
    if grep -q "\-fa on" "$SERVICE_RUN"; then
        echo "  ✅ Сервис с -fa on"
    else
        report_warn "Сервис без -fa on (медленнее ~14%)"
    fi

    # OMP/OPENBLAS threads
    if grep -q "OMP_NUM_THREADS" "$SERVICE_RUN"; then
        echo "  ✅ Сервис с OMP_NUM_THREADS"
    else
        report_warn "Сервис без OMP_NUM_THREADS"
    fi
else
    report_warn "Сервис neon не найден: $SERVICE_RUN"
fi
echo ""

# ─── 5. Loop: cache vs loop-v0.3.sh ───
echo "─── Loop ───"

LOOP3="$HOME/rumix/loop/loop-v0.3.sh"
if [ -f "$LOOP3" ]; then
    if grep -q "CACHE_MAX_LINES" "$LOOP3"; then
        echo "  ✅ CACHE_MAX_LINES в loop-v0.3.sh"
    else
        report_warn "CACHE_MAX_LINES отсутствует в loop-v0.3.sh"
    fi

    if grep -q "consent_check" "$LOOP3"; then
        echo "  ✅ consent_check в loop-v0.3.sh"
    else
        report_warn "consent_check отсутствует в loop-v0.3.sh"
    fi
else
    report_warn "loop-v0.3.sh отсутствует"
fi
echo ""

# ─── ИТОГ ───
echo "═══════════════════════════════════════"
if [ "$issues" -eq 0 ] && [ "$warnings" -eq 0 ]; then
    echo "✅ Config Drift: чисто. Все конфиги согласованы."
    exit 0
elif [ "$issues" -eq 0 ]; then
    echo "⚠️  Config Drift: $warnings предупреждений, 0 ошибок."
    exit 0
else
    echo "❌ Config Drift: $issues ошибок, $warnings предупреждений."
    echo ""
    echo "Что делать: проверь пути и ключи выше. Скорее всего — файл перенесён, но скрипт не обновлён."
    exit 1
fi
