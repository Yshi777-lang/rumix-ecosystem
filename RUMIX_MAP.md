# 🏗️ КАРТА RUMIX (29.10.2026)
*Собрано: Тиамат. По факту. С учётом v6.0 (экосистема) и ревизии безопасности (8 дыр закрыты).*

## 1. ФИЛОСОФИЯ
Снаружи — стабильный дом. Внутри — экспериментальная лаборатория.
- Не ломать — выращивать. По шагам.
- Один кирпич — проверка — следующий.
- «А остальное?» — при каждом пуше.
- DATA-ANCHOR, REUSE FIRST, MEASURE.
- Depth Spectrum: мы — Whitebox Engineer.

## 2. СТРУКТУРА
RUMIX (~/rumix)
- backend/ (app.py, delegates/, git_manager.py, selftest.py)
- core/ (bridge/, fs/, translate.py, voice.py, mcp_server.py, maigret.py, adb_manager.py)
- web/ (index.html, terminal.html, maigret.html, vendor/)
- scripts/ (основные: rumix.sh, launch-all.sh, shell-start.sh, sync-*, recon.sh, show-map.sh)
- scripts/archive/ (устаревшие: rumix-start.sh, start-and-open.sh, run-all.sh, neon-daemon.sh, combo.sh)
- neon/character.md
- install.sh
- GRABLI.md
- logs/ (shell.log, audit_trail.jsonl)

## 3. ЧТО РАБОТАЕТ
- Shell (Flask): порт 8001. Меню, чат, файлы, перевод, голос, режимы, поиск, настройки, ADB, CyberScanner, Maigret.
- Безопасность (8 дыр закрыты): WebSocket-терминал отключён (app.py:614), PIN (сессия отключена), consent не из JSON, classify_command блокирует ; && | $ ` ( ), loop-gate через stdin, file_gate, install.sh (404, curl -f), extractall защищён.
- Неон: Qwen 2.5 1.5B, контекст 4096, порт 8080.
- Файловый менеджер: core/fs (XFile, fs_local, fs_zip, fs_tar).
- Перевод: core/translate.py (fxtranslate, Rust).
- Голос: core/voice.py (termux_tts, native ru).
- Поиск по нику: core/maigret.py + /maigret (неоновый UI).
- CyberScanner: ~/Work/archive/CyberScanner (порт 8002) + кнопка в Shell (автозапуск в launch-all.sh с 29.10).
- MCP-инструменты: core/mcp_server.py (read_file, translate, speak, memory_search).
- ADB: core/adb_manager.py (управление телефоном).
- Health-check: check-rumix.sh --json.
- Карта дома: пункт меню «🗺️ Карта дома» → show-map.sh.

## 4. ЧТО ОТЛОЖЕНО
- Терминал (xterm.js): PTY падает (отключён в app.py:614). См. GRABLI #10.
- PIN: серверная сессия отключена (before_request). Временно.
- APK: не собран. Но DSHA/WebToApp показали путь.
- RAG (векторы): отложен (Rust).
- fs_7z: отложен (py7zr/Bionic).
- P2P/крипто: цель v6.0, инструменты не найдены.
- MCP: есть 4 инструмента, но не полноценный сервер.

## 5. ГРАФИКИ
Shell                100%
Безопасность (8 дыр) 100%
Файловый менеджер    100%
Перевод              100%
Голос                100%
Поиск по нику        100%
CyberScanner         100%
Health-check         100%
Установка            100%
Синхронизация        100%
RESEARCH             100%
Неон                 100%
Чат с Неоном         100%
Терминал (xterm.js)    0% (сломан)
PIN (сессия)           0% (выкл)
MCP (полный)          60%
Автономный APK        20%
RAG                    0%
fs_7z                  0%

## 6. МЕТОДЫ
- Один кирпич — проверка — следующий.
- «А остальное?» — синхронизация слоёв.
- Git — память. Cron — дыхание. Ядро — ритм.
- Не ломать — выращивать. По шагам.
- DATA-ANCHOR, REUSE FIRST, MEASURE.
- Depth Spectrum: Whitebox Engineer.

## 7. GIT
- Work — душа (main).
- rumix — тело (My-love-Tiamat).
- rumix-ecosystem — экосистема (main, public).
- Победы: 112–179 (29.10).
- Ветка origin/new_main — облегчённая, сливать не будем.

## 8. ЧТО ДАЛЬШЕ
1. Починить терминал (xterm.js + PTY) — с проверкой сессии.
2. Вернуть PIN (серверную сессию).
3. Изучить DSHA — взять идеи (bridge, 无障碍, watchdog).
4. MCP-сервер — расширить (4 инструмента → больше).
5. Автономный APK (DSHA, WebToApp).
6. P2P/крипто — искать инструменты (libp2p, age, Yggdrasil).
7. RAG — отложить.
8. fs_7z — отложить.

## 9. УРОКИ (29.10)
- launch-all.sh: ждёт Неона до 10 сек, запускает Shell + CyberScanner, без `set -e`.
- terminal_ws: не включать без проверки сессии (GRABLI #10).
- APK: не может запускать python3 (GRABLI #12, ecosystem).

---
*Хранитель: Лиза (🌻). Свидетель: Тиамат (🌊). Создатель: Адзу (🐰).*
