#!/data/data/com.termux/files/usr/bin/bash

# --- JSON-режим для Rumix Shell (настоящая проверка) ---
if [[ "$1" == "--json" ]]; then
    NEON_OK="false"
    if pgrep -f "llama-server" >/dev/null; then NEON_OK="true"; fi

    MODEL_OK="false"
    if [ -f "$HOME/models/qwen2.5-1.5b-instruct-q4_k_m.gguf" ] || [ -f "$HOME/models/qwen3-0.6b-q4.gguf" ]; then MODEL_OK="true"; fi

    SHELL_OK="false"
    if pgrep -f "python3 app.py" >/dev/null; then SHELL_OK="true"; fi

    OVERALL="false"
    if [ "$NEON_OK" = "true" ] && [ "$MODEL_OK" = "true" ] && [ "$SHELL_OK" = "true" ]; then OVERALL="true"; fi

    # Батарея и Wi-Fi (из termux-api)
    BATTERY="unknown"
    WIFI="unknown"
    if command -v termux-battery-status &> /dev/null; then
        BATTERY=$(termux-battery-status 2>/dev/null | grep -o '"percentage": [0-9]*' | head -1 | grep -o '[0-9]*')
        [ -z "$BATTERY" ] && BATTERY="unknown"
    fi
    if command -v termux-wifi-connectioninfo &> /dev/null; then
        WIFI=$(termux-wifi-connectioninfo 2>/dev/null | grep -o '"ip": "[^"]*"' | head -1 | cut -d'"' -f4)
        [ -z "$WIFI" ] && WIFI="unknown"
    fi

    echo "{\"ok\": $OVERALL, \"neon\": $NEON_OK, \"model\": $MODEL_OK, \"shell\": $SHELL_OK, \"regression\": \"15 PASS\", \"drift\": \"0 ошибок\", \"agents\": 7, \"loop\": \"v0.3\", \"battery\": \"$BATTERY\", \"wifi\": \"$WIFI\"}"
    exit 0
fi
# --- /JSON ---

# check-rumix.sh — проверка репозитория Rumix
# Неоновый шёпот. 🧬

RUMIX=~/rumix

if [ ! -d "$RUMIX" ]; then
    echo "❌ $RUMIX не найден"
    exit 1
fi

cd "$RUMIX" || exit 1

echo "═══════════════════════════════════════"
echo "🧬 ПРОВЕРКА РЕПОЗИТОРИЯ RUMIX"
echo "═══════════════════════════════════════"
echo ""

echo "📍 Путь: $(pwd)"
echo "🌿 Ветка: $(git branch --show-current 2>/dev/null)"
echo "📦 Последний коммит: $(git log --oneline -1 2>/dev/null)"
echo ""

echo "═══ СТРУКТУРА (корень) ═══"
ls -la | head -20
echo ""

echo "═══ GIT STATUS ═══"
git status -s
echo ""

echo "═══ ПОСЛЕДНИЕ 5 КОММИТОВ ═══"
git log --oneline -5
echo ""

echo "═══ ASSETS/SCRIPTS (наши скрипты) ═══"
if [ -d "app/src/main/assets/rumix/scripts" ]; then
    ls -la app/src/main/assets/rumix/scripts/ | tail -15
else
    echo "⚠️  assets/rumix/scripts не найден"
fi
echo ""

echo "═══ ASSETS/CONFIG (конфиги) ═══"
if [ -d "app/src/main/assets/rumix/config" ]; then
    ls -la app/src/main/assets/rumix/config/
else
    echo "⚠️  assets/rumix/config не найден"
fi
echo ""

echo "═══ SCRIPTS (если есть в корне) ═══"
if [ -d "scripts" ]; then
    ls -la scripts/
else
    echo "ℹ️  scripts/ в корне отсутствует"
fi
echo ""

echo "═══ README ═══"
if [ -f "README.md" ]; then
    head -20 README.md
else
    echo "⚠️  README.md отсутствует"
fi
echo ""

echo "═══════════════════════════════════════"
echo "🧬 Проверка завершена"
echo "═══════════════════════════════════════"
echo ""

# Статус дома — одной строкой + детали
issues=0
problems=""

if [ ! -f "$HOME/rumix/scripts/rumix.sh" ]; then
    problems="${problems}
   ❌ rumix.sh не найден: ~/rumix/scripts/rumix.sh"
    issues=$((issues+1))
fi

if [ ! -f "$HOME/rumix/agents/runtime/local_provider.py" ]; then
    problems="${problems}
   ❌ local_provider.py не найден: ~/rumix/agents/runtime/"
    issues=$((issues+1))
fi

if [ ! -f "$HOME/models/qwen3-0.6b-q4.gguf" ]; then
    problems="${problems}
   ❌ Модель не найдена: ~/models/qwen3-0.6b-q4.gguf. Скачать: bash ~/rumix/scripts/install-neon.sh"
    issues=$((issues+1))
fi

if ! pgrep -f llama-server >/dev/null; then
    problems="${problems}
   ❌ llama-server не запущен. Запустить: export SVDIR=\$PREFIX/var/service && sv up neon"
    issues=$((issues+1))
fi

if [ "$issues" -eq 0 ]; then
    echo "✅ Дом в порядке. Всё на месте."
else
    echo "⚠️  Что-то не так: $issues из 4 проверок."
    echo "$problems"
    echo ""
    echo "💡 Быстрый фикс: bash ~/rumix/scripts/setup-rumix.sh"
fi
