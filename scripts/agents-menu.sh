#!/data/data/com.termux/files/usr/bin/bash
# agents-menu.sh — меню Agent Runtime (Pure Bash Edition)
AGENTS_DIR="$HOME/rumix-ecosystem/agents"
get_current_agent() {
    python3 -c "import sys, os; sys.path.insert(0, '$AGENTS_DIR'); import runtime.agents as a; print(a.CURRENT_AGENT)" 2>/dev/null || echo "neon"
}
list_agents() {
    python3 -c "import sys; sys.path.insert(0, '$AGENTS_DIR'); from runtime.agents import AGENTS; [print(f'{name:10s} — {cfg[\"desc\"]}') for name, cfg in AGENTS.items()]" 2>/dev/null
}
chat_loop() { clear; echo "💬 Чат с Agent Runtime\nДля выхода: /quit\n"; cd "$AGENTS_DIR" && python3 main.py; }
switch_agent() {
    clear; echo "🔄 Выбор агента:"; PS3="👉 Введи номер: "
    local agents_list=(); while IFS= read -r line; do agents_list+=("$line"); done < <(list_agents)
    agents_list+=("⬅ Назад")
    select choice in "${agents_list[@]}"; do
        if [[ -n "$choice" && "$choice" != "⬅ Назад" ]]; then
            local name=$(echo "$choice" | awk '{print $1}')
            python3 -c "import sys; sys.path.insert(0, '$AGENTS_DIR'); from runtime.agents import switch_agent; switch_agent('$name'); print('✅ Агент:', '$name')" 2>/dev/null
            sleep 2
        fi
        break
    done
}
run_pipeline() {
    clear; echo "🏗 Pipeline: architect → neon → reviewer"; read -p "Задача для pipeline: " task
    if [ -n "$task" ]; then
        cd "$AGENTS_DIR" && python3 -c "import sys; sys.path.insert(0, '.'); from runtime.pipeline import pipeline; pipeline('$task'); print('✅ Готово.')"
        read -p "Enter для возврата..."
    fi
}
while true; do
    clear; current=$(get_current_agent)
    echo "================================================="
    echo "           🤖 AGENT RUNTIME (agent: $current)           "
    echo "================================================="
    PS3="👉 Введи номер действия: "
    select choice in "💬 Чат" "🔄 Сменить агента" "🏗 Pipeline" "📋 Список агентов" "🔙 Назад в Rumix" "🚪 Выход"; do
        case "$choice" in
            "💬 Чат") chat_loop; break ;;
            "🔄 Сменить агента") switch_agent; break ;;
            "🏗 Pipeline") run_pipeline; break ;;
            "📋 Список агентов") clear; echo "📋 Доступные агенты:"; list_agents; echo ""; read -p "Enter..."; break ;;
            "🔙 Назад в Rumix"|"🚪 Выход") echo "🤖 До встречи."; exit 0 ;;
            *) echo "⚠️ Неверный выбор." ;;
        esac
    done
done
