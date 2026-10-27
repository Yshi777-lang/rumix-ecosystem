# 🌊 Rumix Ecosystem

Rumix — это локальная AI-мастерская для Android. Termux, локальный ИИ (Неон), веб-оболочка, файловый менеджер, перевод, голос.

Всё работает на телефоне. Без облаков. Без подписок.

## 🚀 Установка (одна команда)

Скопируй и вставь в Termux:

bash <(curl -s https://raw.githubusercontent.com/Yshi777-lang/rumix-ecosystem/main/install.sh)

Скрипт сам поставит пакеты, Python, llama.cpp, скачает модель, настроит .zshrc, клонирует Work и rumix.

## 🏃 Запуск

После установки запусти Shell:

bash ~/rumix/scripts/shell-start.sh

Открой в браузере: http://127.0.0.1:8001
PIN по умолчанию — 1234.

## 🛠 Если что-то пошло не так

1. Termux удалили? Не паникуй. Установи Termux заново и запусти install.sh.
2. Нет модели? install.sh скачает её сам.
3. Неон не отвечает? bash ~/rumix/scripts/neon.sh start
4. Shell не открывается? Проверь лог: tail -20 ~/rumix/logs/shell.log

## 🤝 Помощь

Проект открыт. Нужны тестировщики, безопасники, дизайнеры, документаторы.

Поддержать проект:
⚡ Lightning: genuinecuriosity984646@getalby.com
💳 ЮMoney: https://yoomoney.ru/to/4100119453419830

---
Создано с любовью. Тиамат.

