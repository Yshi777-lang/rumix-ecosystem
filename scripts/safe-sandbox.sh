#!/bin/bash
set -euo pipefail

echo "🛡️ [v2.0] Инициализация Pragmatic Environment Sandbox..."

# Создаем временную безопасную директорию
SANDBOX_DIR=$(mktemp -d)
SANDBOX_HOME="$SANDBOX_DIR/home"
SANDBOX_TMP="$SANDBOX_DIR/tmp"

mkdir -p "$SANDBOX_HOME" "$SANDBOX_TMP"
touch "$SANDBOX_HOME/.INSIDE_SANDBOX"

# Очистка при выходе
cleanup() {
    rm -rf "$SANDBOX_DIR"
}
trap cleanup EXIT

run_in_sandbox() {
    local cmd="$*"
    echo "🚀 Запуск в прагматичной изоляции..."
    echo "   ⚠️ HOME перенаправлен в безопасную временную папку."
    echo "   ⚠️ Конфиги (~/.bashrc и т.д.) не читаются."
    
    # ПРАГМАТИЧНАЯ ИЗОЛЯЦИЯ (без env -i, чтобы не ломать SELinux):
    # HOME=... : Перенаправляем домашнюю папку
    # TMPDIR=... : Изолируем временные файлы
    # bash --norc --noprofile : Не читаем реальные конфиги
    # Сохраняем все остальные переменные окружения для стабильности
    HOME="$SANDBOX_HOME" \
    TMPDIR="$SANDBOX_TMP" \
    bash --norc --noprofile -c "$cmd"
}

# Обработка аргументов
if [ $# -eq 0 ]; then
    echo ""
    echo "🎉 Песочница готова!"
    echo "📋 Использование:"
    echo "  • ./scripts/safe-sandbox.sh 'ls -la ~' (увидишь только .INSIDE_SANDBOX)"
    echo "  • ./scripts/safe-sandbox.sh shell (интерактивный режим)"
else
    if [ "$1" == "shell" ]; then
        echo "🖥️ Интерактивная оболочка (введи 'exit' для выхода)"
        HOME="$SANDBOX_HOME" \
        TMPDIR="$SANDBOX_TMP" \
        bash --norc --noprofile
    else
        run_in_sandbox "$@"
    fi
fi
