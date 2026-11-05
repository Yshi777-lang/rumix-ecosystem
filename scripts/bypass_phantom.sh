#!/bin/bash
set -euo pipefail

echo "🛡️ [v2.0] Анализ и обход Phantom Process Killer..."

# Проверяем версию Android (SDK 31 = Android 12)
SDK_VERSION=$(getprop ro.build.version.sdk)
if [ "$SDK_VERSION" -lt 31 ]; then
    echo "✅ Твоя версия Android ($SDK_VERSION) не подвержена Phantom Killer. Обход не требуется."
    exit 0
fi

echo "⚠️ Обнаружен Android $SDK_VERSION. Phantom Killer активен. Ищем способы обхода..."

# Функция применения настроек
apply_fix() {
    local cmd_prefix="$1"
    echo "🔄 Применяю настройки через: $cmd_prefix"
    
    $cmd_prefix device_config put activity_manager max_phantom_processes 9999
    $cmd_prefix device_config put activity_manager phantom_process_timeout 999999
    
    # Проверка применения
    local current_limit=$($cmd_prefix device_config get activity_manager max_phantom_processes)
    if [ "$current_limit" == "9999" ]; then
        echo "✅ УСПЕХ! Лимит процессов увеличен до 9999. Твои сессии больше не будут убиты."
        return 0
    else
        echo "❌ ОШИБКА: Настройка не применилась. Текущий лимит: $current_limit"
        return 1
    fi
}

# Попытка 1: Shizuku (самый удобный и стабильный способ)
if command -v shizuku &> /dev/null; then
    echo "🔍 Найден Shizuku. Проверяю его статус..."
    if shizuku shell echo "OK" &> /dev/null; then
        apply_fix "shizuku shell"
        exit 0
    else
        echo "⚠️ Shizuku установлен, но не запущен или не выданы права. Запусти приложение Shizuku."
    fi
fi

# Попытка 2: ADB Wireless (резервный вариант)
if command -v adb &> /dev/null; then
    echo "🔍 Найден ADB. Проверяю подключение..."
    if adb shell echo "OK" &> /dev/null; then
        apply_fix "adb shell"
        exit 0
    else
        echo "⚠️ ADB установлен, но устройство не подключено. Выполни 'adb connect <IP>:<PORT>'"
    fi
fi

# Если ничего не сработало
echo ""
echo "🚫 Не удалось применить настройки автоматически."
echo "📋 Инструкция для ручного решения:"
echo "1. Установи приложение 'Shizuku' из Google Play или F-Droid."
echo "2. Запусти его и следуй инструкциям по активации (через Wireless Debugging)."
echo "3. После активации просто запусти этот скрипт снова: ./scripts/bypass_phantom.sh"
exit 1
