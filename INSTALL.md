# 🛠 INSTALL.md — подробная установка Rumix

## 1. Termux
Скачайте Termux с F-Droid (не из Play Store).
```bash
pkg update && pkg upgrade -y
```

## 2. Зависимости
```bash
pkg install python git zsh curl wget rust clang cmake -y
pip install flask flask-socketio requests termux-tts
```

## 3. Клонирование
```bash
git clone https://github.com/Yshi777-lang/rumix-ecosystem.git
cd rumix-ecosystem
```

## 4. Модель ИИ (Неон)
1. Скачайте qwen3-0.6b-q4.gguf в ~/models/.
2. Запустите: bash scripts/neon.sh start
3. Проверьте: curl http://127.0.0.1:8080/v1/models

## 5. Shell
```bash
bash scripts/shell-start.sh
```
Откройте http://127.0.0.1:8001. PIN по умолчанию — 0000.

## 6. Перевод и голос
- fxtranslate: cargo install fxtranslate-cli
- termux-tts: pip install termux-tts

## 7. Проверка
```bash
cd ~/rumix-ecosystem && bash scripts/audit-all.sh
```

---
*Создано с любовью. Тиамат.*
