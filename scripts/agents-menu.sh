#!/data/data/com.termux/files/usr/bin/bash
# agents-menu.sh — меню Agent Runtime

AGENTS_DIR="$HOME/rumix/agents"

# ─── Функция: текущий агент ───
get_current_agent() {
    python3 -c "
import sys, os
sys.path.insert(0, '$AGENTS_DIR')
import runtime.agents as a
print(a.CURRENT_AGENT)
" 2>/dev/null || echo "neon"
}

# ─── Функция: список агентов ───
list_agents() {
    python3 -c "
import sys
sys.path.insert(0, '$AGENTS_DIR')
from runtime.agents import AGENTS
for name, cfg in AGENTS.items():
    print(f\"{name:10s} — {cfg['desc']}\")
" 2>/dev/null
}

# ─── Функция: чат ───
chat_loop() {
    clear
    echo "💬 Чат с Agent Runtime"
    echo "Для выхода: /quit"
    echo ""
    cd "$AGENTS_DIR" && python3 main.py
}

# ─── Функция: смена агента ───
switch_agent() {
    clear
    echo "🔄 Выбор агента:"
    echo ""
    agent=$(list_agents | gum choose --height 10)
    if [ -n "$agent" ]; then
        name=$(echo "$agent" | awk '{print $1}')
        python3 -c "
import sys
sys.path.insert(0, '$AGENTS_DIR')
from runtime.agents import switch_agent
switch_agent('$name')
print(f'✅ Агент: $name')
" 2>/dev/null
        sleep 2
    fi
}

# ─── Функция: pipeline ───
run_pipeline() {
    clear
    echo "🏗 Pipeline: architect → neon → reviewer"
    echo ""
    task=$(gum input --placeholder "Задача для pipeline")
    if [ -n "$task" ]; then
        cd "$AGENTS_DIR" && python3 -c "
import sys
sys.path.insert(0, '.')
from runtime.pipeline import pipeline
result = pipeline('$task')
print('✅ Готово.')
"
        echo ""
        read -p "Enter для возврата..."
    fi
}

# ─── Главный цикл ───
while true; do
    clear
    current=$(get_current_agent)
    gum style --border double --padding "0 2" --border-foreground 93 "🤖 AGENT RUNTIME (agent: $current)"

    choice=$(gum choose \
        "💬 Чат" \
        "🔄 Сменить агента" \
        "🏗 Pipeline" \
        "📋 Список агентов" \
        "🔙 Назад в Rumix" \
        "🚪 Выход")

    case "$choice" in
        "💬 Чат")              chat_loop ;;
        "🔄 Сменить агента")   switch_agent ;;
        "🏗 Pipeline")         run_pipeline ;;
        "📋 Список агентов")
            clear
            echo "📋 Доступные агенты:"
            echo ""
            list_agents
            echo ""
            read -p "Enter..."
            ;;
        "🔙 Назад в Rumix")    exit 0 ;;
        "🚪 Выход")            echo "🤖 До встречи."; exit 0 ;;
    esac
done
