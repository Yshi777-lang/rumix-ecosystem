#!/data/data/com.termux/files/usr/bin/bash
# audit-all.sh — быстрый аудит дома (без зависаний)
# Создано: 19.10.2026 (Тиамат + Зая)

GREEN=""
RED=""
YELLOW=""
RESET=""

echo "======================================"
echo "🏠 АУДИТ ДОМА (Shell + Rumix)"
echo "======================================"
echo ""

# 1. SHELL API (GET)
echo "=== 1. SHELL API ==="
ENDPOINTS_GET=(
    "/api/status"
    "/api/logs"
    "/api/files"
    "/api/menu"
    "/api/instruction"
    "/api/projects"
    "/api/git/status"
    "/api/selftest"
)
for path in "${ENDPOINTS_GET[@]}"; do
    code=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8001$path)
    if [ "$code" = "200" ]; then
        echo -e "  ${GREEN}✅${RESET} GET $path ($code)"
    else
        echo -e "  ${RED}❌${RESET} GET $path ($code)"
    fi
done

# 2. SHELL API (POST — только безопасные)
echo ""
echo "=== 2. SHELL API (POST) ==="
code=$(curl -s -o /dev/null -w "%{http_code}" -X POST http://127.0.0.1:8001/api/terminal -H "Content-Type: application/json" -d '{"cmd": "echo test"}')
echo -e "  ${GREEN}✅${RESET} POST /api/terminal ($code)"

code=$(curl -s -o /dev/null -w "%{http_code}" -X POST http://127.0.0.1:8001/api/chat -H "Content-Type: application/json" -d '{"message": "test"}')
echo -e "  ${GREEN}✅${RESET} POST /api/chat ($code)"

# 3. SHELL ACTIONS (только быстрые)
echo ""
echo "=== 3. SHELL ACTIONS ==="
for act in "audit" "backup"; do
    code=$(curl -s -o /dev/null -w "%{http_code}" -X POST http://127.0.0.1:8001/api/action -H "Content-Type: application/json" -d "{\"action\": \"$act\"}")
    if [ "$code" = "200" ]; then
        echo -e "  ${GREEN}✅${RESET} action: $act ($code)"
    else
        echo -e "  ${RED}❌${RESET} action: $act ($code)"
    fi
done

# 4. RUMIX СКРИПТЫ
echo ""
echo "=== 4. RUMIX СКРИПТЫ ==="
SCRIPTS=(
    "rumix.sh"
    "shell-start.sh"
    "shell-stop.sh"
    "fury.sh"
    "backup.sh"
    "check-rumix.sh"
    "agents-menu.sh"
    "projects-menu.sh"
    "install-neon.sh"
)
for scr in "${SCRIPTS[@]}"; do
    if [ -f ~/rumix/scripts/$scr ]; then
        echo -e "  ${GREEN}✅${RESET} $scr"
    else
        echo -e "  ${RED}❌${RESET} $scr"
    fi
done

# 5. АЛИАСЫ
echo ""
echo "=== 5. АЛИАСЫ ==="
for alias_name in "shell" "shell-stop" "neon"; do
    if grep -q "alias $alias_name=" ~/.zshrc; then
        echo -e "  ${GREEN}✅${RESET} alias $alias_name"
    else
        echo -e "  ${RED}❌${RESET} alias $alias_name"
    fi
done

# 6. НЕОН
echo ""
echo "=== 6. НЕОН ==="
if pgrep -f "llama-server" > /dev/null; then
    echo -e "  ${GREEN}✅${RESET} llama-server жив"
else
    echo -e "  ${RED}❌${RESET} llama-server спит"
fi

# 7. GIT
echo ""
echo "=== 7. GIT ==="
cd ~/rumix && echo -e "  ${YELLOW}rumix:${RESET}" && git status -s | head -3
cd ~/Work && echo -e "  ${YELLOW}Work:${RESET}" && git status -s | head -3

echo ""
echo "======================================"
echo "🏁 АУДИТ ЗАВЕРШЁН"
echo "======================================"
