#!/data/data/com.termux/files/usr/bin/bash
# github-token.sh — управление GitHub PAT 🔑
# Хранение в ~/.config/rumix/secrets/ (chmod 600, вне git)

SECRETS_DIR="$HOME/.config/rumix/secrets"
TOKEN_FILE="$SECRETS_DIR/github.token"
CRED_FILE="$HOME/.git-credentials"

mkdir -p "$SECRETS_DIR"
chmod 700 "$SECRETS_DIR"

# ─── Проверка токена через GitHub API ───
check_token() {
    local token="$1"
    local resp
    resp=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "Authorization: token $token" \
        -H "User-Agent: rumix" \
        "https://api.github.com/user")
    [ "$resp" = "200" ] && return 0 || return 1
}

# ─── Установить токен ───
install_token() {
    echo "🔑 Введи GitHub Personal Access Token (PAT):"
    echo "   Создать: https://github.com/settings/tokens"
    echo ""
    local token
    token=$(gum input --password --placeholder "ghp_... или github_pat_...")
    [ -z "$token" ] && echo "⚠️  Отмена" && return

    echo ""
    echo "🔍 Проверяю токен..."
    if check_token "$token"; then
        echo "$token" > "$TOKEN_FILE"
        chmod 600 "$TOKEN_FILE"
        echo "✅ Токен сохранён в: $TOKEN_FILE"

        # Обновить .git-credentials (для автоматического push)
        # Формат: https://username:token@github.com
        echo "🔍 Получаю username..."
        local user
        user=$(curl -s -H "Authorization: token $token" \
            -H "User-Agent: rumix" \
            "https://api.github.com/user" | grep -o '"login": "[^"]*"' | cut -d'"' -f4)
        if [ -n "$user" ]; then
            echo "👤 Username: $user"
            echo "https://$user:$token@github.com" > "$CRED_FILE"
            chmod 600 "$CRED_FILE"
            echo "✅ .git-credentials обновлён"

            # Включить credential.helper=store
            git config --global credential.helper store
            echo "✅ git настроен на store credentials"
        fi
        echo ""
        echo "🎉 Готово. Теперь push/pull — автоматически."
    else
        echo "❌ Токен не работает. Проверь:"
        echo "   - Срок действия (expiration)"
        echo "   - Права (scopes): repo, workflow"
    fi
}

# ─── Показать текущий ───
show_token() {
    if [ -f "$TOKEN_FILE" ]; then
        local token
        token=$(cat "$TOKEN_FILE")
        echo "🔑 Текущий токен: ${token:0:8}...${token: -4}"
        echo "📂 Файл: $TOKEN_FILE"
        echo ""
        if check_token "$token"; then
            echo "✅ Статус: РАБОТАЕТ"
        else
            echo "❌ Статус: НЕ РАБОТАЕТ (истёк?)"
        fi
    else
        echo "⚠️  Токен не установлен"
    fi
}

# ─── Удалить ───
delete_token() {
    if gum confirm "Удалить токен?"; then
        rm -f "$TOKEN_FILE"
        rm -f "$CRED_FILE"
        echo "✅ Удалено"
    fi
}

# ─── Меню ───
while true; do
    clear
    gum style --border normal --padding "0 2" --border-foreground 93 "🔑 GITHUB TOKEN"

    if [ -f "$TOKEN_FILE" ]; then
        token=$(cat "$TOKEN_FILE")
        echo "Текущий: ${token:0:8}...${token: -4}"
        if check_token "$token" 2>/dev/null; then
            echo "Статус: ✅ работает"
        else
            echo "Статус: ❌ не работает"
        fi
    else
        echo "Статус: ⚠️  не установлен"
    fi
    echo ""

    choice=$(gum choose \
        "🔑 Установить / обновить токен" \
        "👁  Показать текущий" \
        "🗑  Удалить токен" \
        "🔙 Назад" \
        "🚪 Выход")

    case "$choice" in
        "🔑 Установить / обновить токен") install_token; echo ""; read -p "Enter..." ;;
        "👁  Показать текущий")           clear; show_token; echo ""; read -p "Enter..." ;;
        "🗑  Удалить токен")              delete_token; read -p "Enter..." ;;
        "🔙 Назад") exit 0 ;;
        "🚪 Выход") echo "🔑 До встречи."; exit 0 ;;
    esac
done
