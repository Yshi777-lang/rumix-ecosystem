#!/data/data/com.termux/files/usr/bin/bash
# rumix-pin.sh — PIN-защита Rumix
# Хранит SHA-256 PIN в ~/.rumix-pin

PIN_FILE="$HOME/.rumix-pin"
SESSION_FILE="$HOME/.rumix-session"
SESSION_TIMEOUT_MIN="${SESSION_TIMEOUT_MIN:-30}"

# Установить PIN
pin_set() {
    local pin1 pin2
    read -r -s -p "Введи новый PIN (4-8 цифр): " pin1; echo ""
    read -r -s -p "Повтори PIN: " pin2; echo ""

    if [ "$pin1" != "$pin2" ]; then
        echo "❌ PIN не совпадают"
        return 1
    fi
    if ! echo "$pin1" | grep -qE '^[0-9]{4,8}$'; then
        echo "❌ PIN должен быть 4-8 цифр"
        return 1
    fi

    local hash
    hash=$(printf '%s' "$pin1" | sha256sum | awk '{print $1}')
    echo "$hash" > "$PIN_FILE"
    chmod 600 "$PIN_FILE"
    echo "✅ PIN установлен"
}

# Проверить PIN
pin_check() {
    [ ! -f "$PIN_FILE" ] && return 0

    # Проверить сессию
    if [ -f "$SESSION_FILE" ]; then
        local last now elapsed
        last=$(cat "$SESSION_FILE" 2>/dev/null || echo 0)
        now=$(date +%s)
        elapsed=$((now - last))
        if [ "$elapsed" -lt "$((SESSION_TIMEOUT_MIN * 60))" ]; then
            date +%s > "$SESSION_FILE"
            return 0
        fi
    fi

    local pin hash stored
    read -r -s -p "🔐 PIN: " pin; echo ""
    hash=$(printf '%s' "$pin" | sha256sum | awk '{print $1}')
    stored=$(cat "$PIN_FILE" 2>/dev/null)

    if [ "$hash" != "$stored" ]; then
        echo "❌ Неверный PIN"
        return 1
    fi

    date +%s > "$SESSION_FILE"
    chmod 600 "$SESSION_FILE"
    echo "✅ Добро пожаловать"
    return 0
}

# Снять PIN
pin_remove() {
    if [ ! -f "$PIN_FILE" ]; then
        echo "ℹ️  PIN не установлен"
        return 0
    fi
    read -r -p "Убрать PIN? (y/n): " confirm
    [ "$confirm" != "y" ] && return 1
    rm -f "$PIN_FILE" "$SESSION_FILE"
    echo "✅ PIN снят"
}

case "${1:-}" in
    set) pin_set ;;
    check) pin_check ;;
    remove) pin_remove ;;
    *)
        echo "Использование: rumix-pin.sh [set|check|remove]"
        exit 1
        ;;
esac
