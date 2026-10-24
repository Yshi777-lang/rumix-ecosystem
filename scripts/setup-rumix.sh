#!/data/data/com.termux/files/usr/bin/bash
# setup-rumix.sh — установка интерфейса Rumix
# Неоновый шёпот. 🧬

echo "🧬 Установка интерфейса Rumix..."

# 1. Пакеты
echo "📦 Ставлю пакеты..."
pkg update -y > /dev/null 2>&1
pkg upgrade -y > /dev/null 2>&1
pkg install -y zsh gum jq git nano curl wget runit termux-services 2>&1 | tail -3

# 2. motd
echo "🎨 Настраиваю motd..."
cat > /data/data/com.termux/files/usr/etc/motd << 'MOTD_EOF'
Welcome to Rumix!
Неоновый шёпот активен.
Набирай: rumix
MOTD_EOF

# 3. zsh как основной
echo "🐚 Настраиваю zsh..."
grep -q "exec zsh" ~/.bashrc || echo 'exec zsh' >> ~/.bashrc

# 4. .zshrc
echo "📝 Создаю .zshrc..."
cat > ~/.zshrc << 'ZSHRC_EOF'

# ==============================
# RUMIX — наш дом
# ==============================

setopt PROMPT_SUBST
export PS1='%F{magenta}➜  %F{cyan}%1~%F{white} $(git branch --show-current 2>/dev/null | sed "s/^/git:(/;s/$/)/") %F{white}'

alias rw='cd ~/Work'
alias rg='cd ~/Work && git status'
alias rumix='bash ~/rumix/scripts/rumix.sh'
alias session-load='bash ~/rumix/scripts/session-load.sh'
alias notes='cd ~/Work/notes'
alias scripts='cd ~/rumix/scripts'
alias setup-rumix='bash ~/rumix/scripts/setup-rumix.sh'
alias install-neon='bash ~/rumix/scripts/install-neon.sh'

echo "Rumix готов. Неоновый шёпот активен. 🧬"

# ==============================
# termux-services (runsvdir + SVDIR)
# ==============================
if [ -f "$PREFIX/etc/profile.d/start-services.sh" ]; then
    . "$PREFIX/etc/profile.d/start-services.sh"
fi

# ==============================
# RUMIX — bootstrap + auto-setup
# ==============================
if [ ! -f ~/.rumix-setup-done ]; then
    if [ ! -d ~/rumix/.git ]; then
        echo "🧬 Rumix: клонирую репо..."
        timeout 300 git clone -b My-love-Tiamat https://github.com/Yshi777-lang/rumix.git ~/rumix 2>&1 | tail -3
    fi
    if [ ! -d ~/Work/.git ]; then
        echo "📁 Work: клонирую репо..."
        timeout 300 git clone https://github.com/Yshi777-lang/Work.git ~/Work 2>&1 | tail -3
    fi
    if [ -f ~/rumix/scripts/setup-rumix.sh ]; then
        bash ~/rumix/scripts/setup-rumix.sh
    fi
fi
ZSHRC_EOF

# 5. Копируем скрипты из assets (если запущено из APK)
echo "📁 Копирую скрипты..."
ASSETS_DIR="/data/data/com.termux/files/home/storage/shared/rumix-assets"
if [ -d "$ASSETS_DIR/scripts" ]; then
    mkdir -p ~/rumix/scripts ~/Work/notes ~/rumix/neon
    cp -r "$ASSETS_DIR/scripts/"* ~/rumix/scripts/ 2>/dev/null
    cp -r "$ASSETS_DIR/config/"* ~/Work/ 2>/dev/null
    chmod +x ~/rumix/scripts/*.sh 2>/dev/null
    echo "✅ Скрипты скопированы из assets"
else
    echo "⚠️  assets не найдены. Клонирую дом из GitHub..."
    cd ~ || exit 1
    # Work
    if [ ! -d ~/Work/.git ]; then
        echo "📁 Клонирую Work..."
        timeout 300 git clone https://github.com/Yshi777-lang/Work.git ~/Work 2>&1 | tail -3
    else
        echo "✅ Work уже есть."
        cd ~/Work && git pull 2>&1 | tail -2
    fi
    # rumix (ветка My-love-Tiamat)
    if [ ! -d ~/rumix/.git ]; then
        echo "📁 Клонирую rumix..."
        timeout 300 git clone -b My-love-Tiamat https://github.com/Yshi777-lang/rumix.git ~/rumix 2>&1 | tail -3
    else
        echo "✅ rumix уже есть."
        cd ~/rumix && git pull 2>&1 | tail -2
    fi
fi

# 6. Флаг setup
touch ~/.rumix-setup-done

echo ""
echo "🧬 Интерфейс Rumix установлен!"
echo "Перезапусти Rumix, чтобы увидеть motd."
echo "Для установки Неона: install-neon"
