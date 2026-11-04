#!/data/data/com.termux/files/usr/bin/bash
# integrity-check.sh — полный аудит целостности дома.

BASE="$HOME/rumix-ecosystem"
echo "🏥 АУДИТ ЦЕЛОСТНОСТИ ДОМА"
echo "═══════════════════════════════════════════════"
echo "📂 База: $BASE"
echo ""

# 1. Подсчёт файлов
SH_COUNT=$(find "$BASE" -name "*.sh" -not -path "*/archive/*" | wc -l)
PY_COUNT=$(find "$BASE" -name "*.py" -not -path "*/__pycache__/*" | wc -l)
KT_COUNT=$(find "$BASE" -name "*.kt" | wc -l)
echo "📊 Статистика:"
echo "   🔧 .sh: $SH_COUNT"
echo "   🐍 .py: $PY_COUNT"
echo "   ☕ .kt: $KT_COUNT"
echo ""

# 2. Проверка синтаксиса Bash
echo "🔍 Проверка синтаксиса Bash..."
BASH_ERRORS=0
for f in $(find "$BASE" -name "*.sh" -not -path "*/archive/*"); do
    if ! bash -n "$f" 2>/dev/null; then
        echo "   ❌ Ошибка синтаксиса: ${f#$BASE/}"
        BASH_ERRORS=$((BASH_ERRORS+1))
    fi
done
if [ "$BASH_ERRORS" -eq 0 ]; then
    echo "   ✅ Все скрипты синтаксически верны."
else
    echo "   ⚠️ Найдено ошибок: $BASH_ERRORS"
fi
echo ""

# 3. Поиск старых путей (только в активных файлах)
echo "🔍 Поиск старых путей (~/rumix/)..."
OLD_PATHS=$(grep -rn "~/rumix/\|\$HOME/rumix/" --include="*.sh" --include="*.py" --include="*.kt" "$BASE" 2>/dev/null | grep -v "rumix-ecosystem" | grep -v "/archive/" | grep -v "/add_" | grep -v "/inject_")
if [ -z "$OLD_PATHS" ]; then
    echo "   ✅ Старых путей не найдено. Дом един."
else
    echo "   ⚠️ Найдены старые пути:"
    echo "$OLD_PATHS" | head -5 | sed "s|$BASE/|      |g"
fi
echo ""

# 4. Проверка ключевых файлов
echo "🔍 Проверка ключевых файлов..."
FILES=("backend/app.py" "core/modules/__init__.py" "scripts/rumix.sh" "scripts/launch-all.sh" "scripts/neon.sh")
for f in "${FILES[@]}"; do
    if [ -f "$BASE/$f" ]; then
        echo "   ✅ $f"
    else
        echo "   ❌ $f (отсутствует)"
    fi
done
echo ""

# 5. Проверка запущенных процессов
echo "🔍 Проверка процессов..."
if pgrep -f "python.*app.py" > /dev/null; then
    echo "   ✅ Shell (Flask) жив"
else
    echo "   ⚠️ Shell (Flask) спит"
fi
if pgrep -f "llama-server" > /dev/null; then
    echo "   ✅ Неон (llama-server) жив"
else
    echo "   ⚠️ Неон (llama-server) спит"
fi
echo ""

echo "═══════════════════════════════════════════════"
echo "🏁 Аудит завершён."
