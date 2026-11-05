#!/data/data/com.termux/files/usr/bin/bash
# install.sh — установка дома одной командой. Можно запускать повторно.

REPO_DIR=$(cd "$(dirname "$0")" && pwd)
DATA_DIR="${RUMIX_DATA_DIR:-$HOME/rumix}"
UPDATE=0
[ "${1:-}" = "--update" ] && UPDATE=1

step() { printf '\n%s\n' "$1"; }
warn() { printf '  ⚠️  %s\n' "$1"; }

echo "🌊 Rumix — установка"
echo "   код:    $REPO_DIR"
echo "   данные: $DATA_DIR"

step "1. Проверка Termux"
if [ ! -d /data/data/com.termux ]; then
    echo "  ❌ Это не Termux. Нужен Termux с F-Droid."
    exit 1
fi
echo "  ✅ Termux"

step "2. Пакеты"
if [ "$UPDATE" = "1" ]; then
    echo "  ⏳ pkg update..."
    pkg update -y || warn "pkg update завершился с ошибкой — продолжаю"
fi

if pkg install -y python git zsh curl wget jq termux-api termux-services; then
    echo "  ✅ базовые пакеты"
else
    echo "  ❌ не поставились базовые пакеты — дальше нет смысла"
    exit 1
fi

OPT_FAIL=""
OPT_OK=0
for p in llama-cpp rust clang cmake zip ffmpeg dnsutils; do
    if pkg install -y "$p" >/dev/null 2>&1; then
        OPT_OK=$((OPT_OK + 1))
    else
        OPT_FAIL="$OPT_FAIL $p"
    fi
done
if [ -n "$OPT_FAIL" ]; then
    warn "не встали:$OPT_FAIL — это не блокер"
else
    echo "  ✅ опциональные пакеты ($OPT_OK)"
fi

step "3. Python-зависимости"
if [ -f "$REPO_DIR/requirements.txt" ]; then
    if pip install -q -r "$REPO_DIR/requirements.txt"; then
        echo "  ✅ requirements.txt"
    else
        echo "  ❌ pip не смог поставить зависимости"
        exit 1
    fi
else
    warn "нет requirements.txt — ставлю минимум"
    pip install -q flask flask-socketio requests termux-tts || exit 1
fi
pip install -q maigret >/dev/null 2>&1 && echo "  ✅ maigret (поиск по нику)" \
    || warn "maigret не поставился — карточка «Поиск» останется пустой"

step "4. Репозиторий rumix"
if [ -d "$DATA_DIR" ]; then
    echo "  ✅ уже есть: $DATA_DIR"
else
    git clone -b My-love-Tiamat https://github.com/Yshi777-lang/rumix.git "$DATA_DIR" \
        && echo "  ✅ склонирован" || warn "не склонировался — дом будет без архива/логов"
fi
mkdir -p "$DATA_DIR/logs" "$DATA_DIR/run" "$DATA_DIR/agents"

step "5. Оболочка"
if [ ! -f "$HOME/.zshrc" ] && [ -f "$REPO_DIR/zshrc.backup" ]; then
    cp "$REPO_DIR/zshrc.backup" "$HOME/.zshrc" && echo "  ✅ .zshrc из zshrc.backup"
else
    echo "  ✅ .zshrc не трогаю"
fi

step "6. Модель Неона"
mkdir -p "$HOME/models"
MODEL="$HOME/models/qwen2.5-1.5b-instruct-q4_k_m.gguf"
if [ -f "$MODEL" ]; then
    echo "  ✅ модель уже есть"
else
    echo "  ⏳ качаю Qwen2.5 1.5B (~1 ГБ)..."
    curl -fL --progress-bar -o "$MODEL" \
        "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf" \
        && echo "  ✅ модель скачана" || warn "модель не скачалась — Неон не запустится"
fi

step "7. Токен установки"
if [ -f "$HOME/.rumix_token" ]; then
    echo "  ✅ токен уже есть: ~/.rumix_token"
else
    python3 - <<'PY'
import os, pathlib, secrets
p = pathlib.Path.home() / ".rumix_token"
p.write_text(secrets.token_urlsafe(32) + "\n", encoding="utf-8")
os.chmod(p, 0o600)
print("  ✅ создан ~/.rumix_token (600)")
PY
fi

step "8. Сервисы"
if [ -f "$REPO_DIR/scripts/svc-manager.sh" ]; then
    bash "$REPO_DIR/scripts/svc-manager.sh" install || warn "сервисы не установились"
else
    warn "нет scripts/svc-manager.sh"
fi

step "9. Проверка дома"
bash "$REPO_DIR/scripts/doctor.sh"

TOKEN=$(cat "$HOME/.rumix_token" 2>/dev/null)
step "ГОТОВО"
echo "  Дальше:"
echo "    1) bash $REPO_DIR/scripts/shell-start.sh"
echo "    2) поставь APK и введи токен (долгое нажатие на чип статуса)"
echo "       адрес: 127.0.0.1:8001"
[ -n "$TOKEN" ] && echo "       токен: $TOKEN"
echo "    3) Неон: bash $REPO_DIR/scripts/neon.sh start"
echo ""
echo "  Диагностика в любой момент: bash $REPO_DIR/scripts/doctor.sh"
