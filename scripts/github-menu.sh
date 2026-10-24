#!/data/data/com.termux/files/usr/bin/bash
# github-menu.sh — меню GitHub 🐙
# Концентрат всех git-операций дома.

WORK="$HOME/Work"
RUMIX="$HOME/rumix"

# ─── Функция: выбрать репо ───
pick_repo() {
    gum choose "🌿 Work (душа)" "🧬 Rumix (тело)" "🔙 Назад"
}

# ─── Функция: выполнить в репо ───
run_in() {
    local repo="$1"
    local cmd="$2"
    cd "$repo" && eval "$cmd"
}

while true; do
    clear
    gum style --border double --padding "0 2" --border-foreground 93 "🐙 GITHUB — МЕНЮ"

    choice=$(gum choose \
        "📥 Pull (скачать)" \
        "📤 Push (загрузить)" \
        "📋 Status (что изменилось)" \
        "📜 Log (история)" \
        "🔀 Ветки" \
        "🔑 Токен / API" \
        "🌐 Открыть репо" \
        "🚪 Выход")

    case "$choice" in
        # ═══ PULL ═══
        "📥 Pull (скачать)")
            repo=$(pick_repo)
            case "$repo" in
                "🌿 Work (душа)")   run_in "$WORK" "git pull origin main" ;;
                "🧬 Rumix (тело)")  run_in "$RUMIX" "git pull origin My-love-Tiamat" ;;
                "🔙 Назад") continue ;;
            esac
            echo ""; read -p "Enter..."
            ;;

        # ═══ PUSH ═══
        "📤 Push (загрузить)")
            repo=$(pick_repo)
            case "$repo" in
                "🌿 Work (душа)")
                    cd "$WORK"
                    git status -s
                    echo ""
                    msg=$(gum input --placeholder "Сообщение коммита (Enter = auto)")
                    [ -z "$msg" ] && msg="auto $(date +%d.%m_%H:%M)"
                    git add -A && git commit -m "$msg" && git push origin main
                    ;;
                "🧬 Rumix (тело)")
                    cd "$RUMIX"
                    git status -s
                    echo ""
                    msg=$(gum input --placeholder "Сообщение коммита (Enter = auto)")
                    [ -z "$msg" ] && msg="auto $(date +%d.%m_%H:%M)"
                    git add -A && git commit -m "$msg" && git push origin My-love-Tiamat
                    ;;
                "🔙 Назад") continue ;;
            esac
            echo ""; read -p "Enter..."
            ;;

        # ═══ STATUS ═══
        "📋 Status (что изменилось)")
            clear
            echo "═══ 🌿 Work ═══"
            cd "$WORK" && git status -s && git branch --show-current
            echo ""
            echo "═══ 🧬 Rumix ═══"
            cd "$RUMIX" && git status -s && git branch --show-current
            echo ""; read -p "Enter..."
            ;;

        # ═══ LOG ═══
        "📜 Log (история)")
            repo=$(pick_repo)
            case "$repo" in
                "🌿 Work (душа)")
                    clear
                    cd "$WORK" && git log --oneline -15
                    ;;
                "🧬 Rumix (тело)")
                    clear
                    cd "$RUMIX" && git log --oneline -15
                    ;;
                "🔙 Назад") continue ;;
            esac
            echo ""; read -p "Enter..."
            ;;

        # ═══ ВЕТКИ ═══
        "🔀 Ветки")
            clear
            echo "═══ 🌿 Work ═══"
            cd "$WORK" && git branch -a
            echo ""
            echo "═══ 🧬 Rumix ═══"
            cd "$RUMIX" && git branch -a
            echo ""; read -p "Enter..."
            ;;

        # ═══ ТОКЕН / API ═══
        "🔑 Токен / API")
            bash "$HOME/rumix/scripts/github-token.sh"
            ;;

        # ═══ ОТКРЫТЬ РЕПО ═══
        "🌐 Открыть репо")
            repo=$(pick_repo)
            case "$repo" in
                "🌿 Work (душа)")
                    termux-open-url "https://github.com/Yshi777-lang/Work"
                    ;;
                "🧬 Rumix (тело)")
                    termux-open-url "https://github.com/Yshi777-lang/rumix"
                    ;;
                "🔙 Назад") continue ;;
            esac
            ;;

        # ═══ ВЫХОД ═══
        "🚪 Выход")
            echo "🐙 До встречи, папа."
            exit 0
            ;;
    esac
done
