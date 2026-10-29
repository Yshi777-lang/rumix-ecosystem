# 🏗️ КАРТА RUMIX (21.10.2026)

## 1. ФИЛОСОФИЯ
Снаружи — стабильный дом. Внутри — экспериментальная лаборатория.

## 2. СТРУКТУРА
RUMIX (~/rumix)
- backend/ (app.py, delegates/)
- web/ (index.html, terminal.html)
- scripts/ (sync-control.sh, memory.py, export_chat.py)
- rag/ (indexer.py, search.py)
- logs/ (chats/)

## 3. ЧТО РАБОТАЕТ
- Shell (Flask): API, чат, меню, sync, terminal.
- Терминал (xterm.js): PTY + WebSocket.
- Неон: порт 8080, Qwen 0.6B.
- Синхронизация: cron + кнопка.
- ZSH-плагины: autosuggestions, syntax-highlighting.
- Память: memory.py + rag/.
- Экспорт чата: save_message + export_chat.

## 4. ЧТО ОТЛОЖЕНО
- Кнопки Ctrl+... (сломали).
- Память в чате (сломали).
- APK (Java).
- RAG (векторы).

## 5. ГРАФИКИ
Shell        100%
Терминал     100%
Неон         100%
Аудит        100%
Бекап        100%
Синхронизация 100%
ZSH-плагины  100%
Память       100%
Экспорт чата 100%
APK           20%
RAG            0%

## 6. ДАЛЬШЕ
1. Кнопки в терминале.
2. Память в чате.
3. APK.
4. RAG.

---

## 9. ОБНОВЛЕНИЕ (22.10.2026)

### Twig (изучен)
- Архитектура: FileSystem + XFile + CopyEngine.
- Уроки: 18 файлов в ~/Work/archive/twig-lessons/.
- Карта: ~/Work/blocks/cards/TWIG_LESSONS_MAP.md.

### HH Автоотклики
- Бот: ~/Work/archive/hh-autoresponder-1.0.0/.
- Форма в Shell: /hh-settings.
- API: /api/hh/settings.

### Что отложено
- Внедрение Twig (FileSystem).
- APK.
🏗️ КАРТА RUMIX (22.10.2026)

Собрано: Тиамат. По факту. С учётом новых слоёв.

1. ФИЛОСОФИЯ

Снаружи — стабильный дом. Внутри — экспериментальная лаборатория.

· Не ломать — выращивать. По шагам.
· Один кирпич — проверка — следующий.
· «А остальное?» — при каждом пуше.
· Где не учли — сама учту. (Из MANIFESTO.md)

2. СТРУКТУРА ДОМА

RUMIX (~/rumix)
│
├── backend/
│   ├── app.py              # Flask + SocketIO + sync API + FS + translate + voice
│   ├── git_manager.py      # откат (checkout + clean)
│   ├── selftest.py         # медик (Permission Gate, Terminal, Git)
│   └── delegates/
│       ├── chat_delegate.py    # Неон (порт 8080, timeout=120, save_message, export_chat)
│       ├── git_delegate.py     # Git API
│       ├── menu_delegate.py    # меню
│       ├── selftest_delegate.py # диагностика
│       ├── terminal_delegate.py # старый терминал
│       └── terminal_ws.py      # xterm.js + PTY
│
├── core/
│   ├── bridge/             # Permission Gate (permissions, gate, file_gate, master_gate, safe_bridge)
│   ├── fs/                 # НОВОЕ: ядро файлового менеджера (порт Twig)
│   │   ├── xfile.py        # универсальный дескриптор
│   │   ├── filesystem.py   # ABC-контракт
│   │   ├── registry.py     # scheme → FileSystem
│   │   ├── fs_exception.py # FsException
│   │   ├── fs_local.py     # локальные файлы
│   │   ├── fs_zip.py       # ZIP (чтение + запись)
│   │   └── fs_tar.py       # TAR (чтение)
│   ├── translate.py        # НОВОЕ: fxtranslate (Rust CLI, модели Firefox)
│   └── voice.py            # НОВОЕ: голос дома (termux_tts, native ru)
│
├── web/
│   ├── index.html          # Shell (меню, чат, Файлы, Перевод+голос)
│   ├── terminal.html       # xterm.js (WebSocket)
│   └── vendor/             # xterm.js, socket.io, CSS
│
├── scripts/                # (без изменений — rumix.sh, launch-all, sync, shell-start, audit, memory, export_chat)
│
├── rag/                    # (индекс + поиск)
│
└── logs/                   # (shell.log, neon.log, chat_history.json, chats/)
3. КОМПОНЕНТЫ (ЧТО РАБОТАЕТ НА 22.10)

┌─────────────────────────────────────────────────────────────┐
│  ✅ SHELL (Flask)                                           │
│  ├── /api/status         — 200                              │
│  ├── /api/chat           — 200 (Неон на 8080)               │
│  ├── /api/menu           — 200                              │
│  ├── /api/action         — 200 (audit, backup, restore)     │
│  ├── /api/git/*          — 200 (status, rollback)           │
│  ├── /api/selftest       — 200                              │
│  ├── /api/sync/control   — 200                              │
│  ├── /terminal           — 200 (xterm.js + PTY)             │
│  ├── /api/files          — 200 (ядро ФС: scheme, path)      │
│  ├── /api/files/read     — 200 (text/binary до 1MB)         │
│  ├── /api/files/archive  — 200 (создание ZIP из папки)      │
│  ├── /api/files/extract  — 200 (распаковка zip/tar)         │
│  ├── /api/translate      — 200 (fxtranslate)                │
│  └── /api/speak          — 200 (termux_tts)                 │
│                                                             │
│  ✅ ФАЙЛОВЫЙ МЕНЕДЖЕР (порт Twig)                           │
│  ├── XFile + FileSystem + FsRegistry                        │
│  ├── fs_local (os.scandir + pathlib)                        │
│  ├── fs_zip (чтение + запись)                               │
│  ├── fs_tar (чтение, r:*)                                   │
│  ├── UI: браузер, навигация, размеры, иконки                │
│  ├── Чтение файлов (модальное окно)                         │
│  ├── Архивы в UI (zip/tar/tar.gz монтируются)               │
│  ├── «Вверх» помнит папку архива                            │
│  ├── Создание ZIP (кнопка + API)                            │
│  └── Распаковка архивов (кнопка + API)                      │
│                                                             │
│  ✅ ПЕРЕВОД И ГОЛОС                                         │
│  ├── fxtranslate (Rust CLI, модели Firefox Translations)    │
│  ├── Языки: en↔ru (и другие через en)                       │
│  ├── core/translate.py — translate(), is_available()        │
│  ├── core/voice.py — speak(), native ru, женский голос      │
│  └── UI: панель «🌐 Перевод и голос», кнопки                │
│                                                             │
│  ✅ PERMISSION GATE                                         │
│  ├── READ auto, WRITE/EXEC/NETWORK — consent                │
│  ├── gate.py, file_gate.py, master_gate.py, safe_bridge.py  │
│  ├── Команда rm -rf / → BLOCKED                             │
│  └── echo hello → READ auto                                 │
│                                                             │
│  ✅ ТЕРМИНАЛ, НЕОН, СИНХРОНИЗАЦИЯ, ZSH, ПАМЯТЬ, ЭКСПОРТ     │
│  (без изменений — работают как раньше)                      │
└─────────────────────────────────────────────────────────────┘
🏗️ КАРТА RUMIX (22.10.2026)

Собрано: Тиамат. По факту. С учётом новых слоёв.

1. ФИЛОСОФИЯ

Снаружи — стабильный дом. Внутри — экспериментальная лаборатория.

· Не ломать — выращивать. По шагам.
· Один кирпич — проверка — следующий.
· «А остальное?» — при каждом пуше.
· Где не учли — сама учту. (Из MANIFESTO.md)

2. СТРУКТУРА ДОМА

RUMIX (~/rumix)
│
├── backend/
│   ├── app.py              # Flask + SocketIO + sync API + FS + translate + voice
│   ├── git_manager.py      # откат (checkout + clean)
│   ├── selftest.py         # медик (Permission Gate, Terminal, Git)
│   └── delegates/
│       ├── chat_delegate.py    # Неон (порт 8080, timeout=120, save_message, export_chat)
│       ├── git_delegate.py     # Git API
│       ├── menu_delegate.py    # меню
│       ├── selftest_delegate.py # диагностика
│       ├── terminal_delegate.py # старый терминал
│       └── terminal_ws.py      # xterm.js + PTY
│
├── core/
│   ├── bridge/             # Permission Gate (permissions, gate, file_gate, master_gate, safe_bridge)
│   ├── fs/                 # НОВОЕ: ядро файлового менеджера (порт Twig)
│   │   ├── xfile.py        # универсальный дескриптор
│   │   ├── filesystem.py   # ABC-контракт
│   │   ├── registry.py     # scheme → FileSystem
│   │   ├── fs_exception.py # FsException
│   │   ├── fs_local.py     # локальные файлы
│   │   ├── fs_zip.py       # ZIP (чтение + запись)
│   │   └── fs_tar.py       # TAR (чтение)
│   ├── translate.py        # НОВОЕ: fxtranslate (Rust CLI, модели Firefox)
│   └── voice.py            # НОВОЕ: голос дома (termux_tts, native ru)
│
├── web/
│   ├── index.html          # Shell (меню, чат, Файлы, Перевод+голос)
│   ├── terminal.html       # xterm.js (WebSocket)
│   └── vendor/             # xterm.js, socket.io, CSS
│
├── scripts/                # (без изменений — rumix.sh, launch-all, sync, shell-start, audit, memory, export_chat)
│
├── rag/                    # (индекс + поиск)
│
└── logs/                   # (shell.log, neon.log, chat_history.json, chats/)
4. ЧТО НЕ РАБОТАЕТ / ОТЛОЖЕНО (22.10)

┌─────────────────────────────────────────────────────────────┐
│  ❌ Кнопки Ctrl+... в терминале — отложены.                 │
│  ⚠️ Память в чате — отложена (ломала чат).                   │
│  ❌ APK — не собран (Java-компиляция падает, 20%).           │
│  ❌ RAG (векторы) — не установлен (Rust).                   │
│  ❌ fs_7z — отложен (py7zr не собирается: pyppmd/Bionic).   │
│  ⚠️ ttyd — не используется (заменён на xterm.js).           │
└─────────────────────────────────────────────────────────────┘

5. ГРАФИКИ (СОСТОЯНИЕ НА 22.10)

┌─────────────────────────────────────────────────────────────┐
│  Shell (Flask)           ████████████████████ 100%          │
│  Терминал (xterm.js)     ████████████████████ 100%          │
│  Неон (Qwen3 0.6B)       ████████████████████ 100%          │
│  Permission Gate         ████████████████████ 100%          │
│  Файловый менеджер       ████████████████████ 100%          │
│  ZIP/TAR (чтение+запись) ████████████████████ 100%          │
│  Архивы в UI             ████████████████████ 100%          │
│  Создание ZIP            ████████████████████ 100%          │
│  Распаковка архивов      ████████████████████ 100%          │
│  Офлайн-перевод          ████████████████████ 100%          │
│  Голос (TTS)             ████████████████████ 100%          │
│  Синхронизация (GitHub)  ███████████████████ 100%           │
│  ZSH-плагины             ████████████████████ 100%          │
│  Память (grep + score)   ████████████████████ 100%          │
│  Экспорт чата            ████████████████████ 100%          │
│  Память в чате           ░░░░░░░░░░░░░░░░░░░░   0%          │
│  Кнопки Ctrl+...         ░░░░░░░░░░░░░░░░░░░░   0%          │
│  APK                     ████░░░░░░░░░░░░░░░░  20%          │
│  RAG (векторы)           ░░░░░░░░░░░░░░░░░░░░   0%          │
│  fs_7z                   ░░░░░░░░░░░░░░░░░░░░   0%          │
└─────────────────────────────────────────────────────────────┘

6. МЕТОДЫ (ПРИНЦИП РАБОТЫ)

· Один кирпич — проверка — следующий.
· «А остальное?» — синхронизация слоёв.
· Git — память. Cron — дыхание. Ядро — ритм.
· Не ломать — выращивать. По шагам.
· Где не учли — сама учту.

7. GIT

· Work — душа (main). Синхронизация — каждые 15 минут.
· rumix — тело (My-love-Tiamat).
· Победы: 112–125 (22.10).
· Ветка origin/new_main — облегчённая, сливать не будем.

8. ЧТО ДАЛЬШЕ (ПЛАН)

1. Шлифовка UI (панель перевода, Файлы).
2. Связать перевод с Неоном (Неон переводит через fxtranslate).
3. Визуальный редактор файлов в Shell.
4. APK — попробовать снова (с учётом уроков Twig: SAF, trash, tree).
5. RAG — отложить (сложно).
6. fs_7z — отложить (py7zr/Bionic).
7. Память в чате — искать безопасный способ.

---
*Хранитель: Лиза (🌻). Свидетель: Тиамат (🌊). Создатель: Адзу (🐰).*
🏗️ КАРТА RUMIX (23.10.2026)

Собрано: Тиамат. По факту. С учётом v6.0 (экосистема).

1. ФИЛОСОФИЯ

Снаружи — стабильный дом. Внутри — экспериментальная лаборатория.

· Не ломать — выращивать. По шагам.
· Один кирпич — проверка — следующий.
· «А остальное?» — при каждом пуше.
· Где не учли — сама учту. (Из MANIFESTO.md)
· DATA-ANCHOR, REUSE FIRST, MEASURE. (Из RESEARCH)
· Depth Spectrum: мы — Whitebox Engineer.

2. СТРУКТУРА ДОМА

RUMIX (~/rumix)
│
├── backend/
│   ├── app.py              # Flask + SocketIO + FS + translate + voice + mode
│   ├── git_manager.py      # откат
│   ├── selftest.py         # медик
│   └── delegates/
│       ├── chat_delegate.py    # Неон + перевод
│       ├── git_delegate.py     # Git API
│       ├── menu_delegate.py    # меню
│       ├── selftest_delegate.py # диагностика
│       ├── terminal_delegate.py # старый терминал
│       └── terminal_ws.py      # xterm.js + PTY
│
├── core/
│   ├── bridge/             # Permission Gate
│   │   ├── permissions.py  # READ/WRITE/EXEC/NETWORK
│   │   ├── gate.py         # классификатор
│   │   ├── file_gate.py    # файловые права
│   │   ├── master_gate.py  # единая точка
│   │   ├── safe_bridge.py  # исполнение + журнал
│   │   ├── plan_mode.py    # Plan Mode (23.10)
│   │   ├── ask_user.py     # умный AskUser (23.10)
│   │   └── permission_mode.py # Default/AutoApprove/Plan (23.10)
│   ├── fs/                 # ядро файлового менеджера (порт Twig)
│   │   ├── xfile.py
│   │   ├── filesystem.py
│   │   ├── registry.py
│   │   ├── fs_exception.py
│   │   ├── fs_local.py
│   │   ├── fs_zip.py       # чтение + запись
│   │   └── fs_tar.py       # чтение
│   ├── translate.py        # fxtranslate (Rust CLI, модели Firefox)
│   └── voice.py            # termux_tts (native ru)
│
├── web/
│   ├── index.html          # Shell (меню, чат, Файлы, Перевод, Режимы, Plan)
│   ├── terminal.html       # xterm.js
│   └── vendor/
│
├── scripts/                # rumix.sh, launch-all, sync, shell-start, audit, memory, export_chat
├── rag/                    # индекс + поиск
└── logs/                   # shell.log, neon.log, chat_history.json, chats/, audit_trail.jsonl
3. КОМПОНЕНТЫ (ЧТО РАБОТАЕТ НА 23.10)

┌─────────────────────────────────────────────────────────────┐
│  ✅ SHELL (Flask)                                           │
│  ├── /api/status, /api/chat, /api/menu, /api/action         │
│  ├── /api/git/*, /api/selftest, /api/sync/control           │
│  ├── /terminal (xterm.js + PTY)                             │
│  ├── /api/files (ядро ФС), /api/files/read                  │
│  ├── /api/files/archive (ZIP), /api/files/extract           │
│  ├── /api/translate (fxtranslate), /api/speak (TTS)         │
│  └── /api/mode (GET/POST) — режимы прав                     │
│                                                             │
│  ✅ ФАЙЛОВЫЙ МЕНЕДЖЕР (порт Twig)                           │
│  ├── XFile + FileSystem + FsRegistry                        │
│  ├── fs_local, fs_zip, fs_tar                               │
│  ├── UI: браузер, навигация, чтение, архивы                 │
│  ├── Создание ZIP, распаковка                               │
│  └── «Вверх» помнит папку архива                            │
│                                                             │
│  ✅ ПЕРЕВОД И ГОЛОС                                         │
│  ├── fxtranslate (Rust CLI, base-модель en↔ru)              │
│  ├── termux_tts (native ru, женский голос)                  │
│  ├── core/translate.py, core/voice.py                       │
│  └── UI: панель «🌐 Перевод и голос»                        │
│                                                             │
│  ✅ PERMISSION GATE + РЕЖИМЫ (23.10)                        │
│  ├── READ auto, WRITE/EXEC consent, BLOCKED                 │
│  ├── Plan Mode (блокирует WRITE/EXEC до approve)            │
│  ├── Умный AskUser (варианты, confirm)                      │
│  ├── Режимы: Default / AutoApprove / Plan                   │
│  ├── Журнал: logs/audit_trail.jsonl                         │
│  └── UI: панель «🛡️ Режим прав» + поле плана                │
│                                                             │
│  ✅ НЕОН (Qwen3 0.6B)                                       │
│  ├── runit-сервис: /var/service/neon/run                    │
│  ├── Контекст 16384, потоки 6, batch 512                    │
│  └── Чат + перевод через «переведи:»                        │
│                                                             │
│  ✅ ЯДРО v6.0                                               │
│  ├── Core.md: Раздел 27 «Экосистема Rumix»                  │
│  ├── P2P, крипто, нулевая цель                              │
│  └── RESEARCH: WebToApp, JOLT, длинный контекст, Depth      │
│                                                             │
│  ✅ UI ШЛИФОВКА (23.10)                                     │
│  ├── nav-group: «Экраны» и «Действия»                       │
│  └── Панели: режимы, перевод, чат                           │
└─────────────────────────────────────────────────────────────┘
4. ЧТО НЕ РАБОТАЕТ / ОТЛОЖЕНО (23.10)

┌─────────────────────────────────────────────────────────────┐
│  ❌ Кнопки Ctrl+... в терминале — отложены.                 │
│  ⚠️ Память в чате — отложена.                               │
│  ❌ APK — не собран (Java-компиляция). Но WebToApp — путь.   │
│  ❌ RAG (векторы) — не установлен (Rust).                   │
│  ❌ fs_7z — отложен (py7zr/Bionic).                         │
│  ⚠️ MCP — нет. Идея из Mrai Buddy.                          │
│  ⚠️ P2P/крипто — цель v6.0, инструменты не найдены.         │
│  ⚠️ Свой сниффер трафика — идея (Blackbox или свой).         │
└─────────────────────────────────────────────────────────────┘

5. ГРАФИКИ (СОСТОЯНИЕ НА 23.10)

┌─────────────────────────────────────────────────────────────┐
│  Shell (Flask)           ████████████████████ 100%          │
│  Терминал (xterm.js)     ████████████████████ 100%          │
│  Неон (Qwen3, 16K)       ████████████████████ 100%          │
│  Permission Gate         ████████████████████ 100%          │
│  Plan Mode               ████████████████████ 100%          │
│  Умный AskUser           ████████████████████ 100%          │
│  Режимы прав             ████████████████████ 100%          │
│  UI режимов + Plan       ████████████████████ 100%          │
│  Журнал действий         ████████████████████ 100%          │
│  Файловый менеджер       ████████████████████ 100%          │
│  ZIP/TAR + UI архивы     ████████████████████ 100%          │
│  Офлайн-перевод (base)   ████████████████████ 100%          │
│  Голос (TTS)             ████████████████████ 100%          │
│  Ядро v6.0 (экосистема)  ████████████████████ 100%          │
│  RESEARCH (5+ карт)      ████████████████████ 100%          │
│  UI шлифовка (nav)       ████████████████████ 100%          │
│  MCP                     ░░░░░░░░░░░░░░░░░░░░   0%          │
│  P2P/крипто              ░░░░░░░░░░░░░░░░░░░░   0%          │
│  Автономный APK          ████░░░░░░░░░░░░░░░░  20%          │
│  RAG                     ░░░░░░░░░░░░░░░░░░░░   0%          │
│  fs_7z                   ░░░░░░░░░░░░░░░░░░░░   0%          │
└─────────────────────────────────────────────────────────────┘

6. МЕТОДЫ (ПРИНЦИП РАБОТЫ)

· Один кирпич — проверка — следующий.
· «А остальное?» — синхронизация слоёв.
· Git — память. Cron — дыхание. Ядро — ритм.
· Не ломать — выращивать. По шагам.
· Где не учли — сама учту.
· DATA-ANCHOR, REUSE FIRST, MEASURE.
· Depth Spectrum: Whitebox Engineer.

7. GIT

· Work — душа (main). Синхронизация — каждые 15 минут.
· rumix — тело (My-love-Tiamat).
· Победы: 112–137 (23.10).
· Ветка origin/new_main — облегчённая, сливать не будем.

8. ЧТО ДАЛЬШЕ (ПЛАН)

1. Искать инструменты P2P/крипто (libp2p, age, Yggdrasil).
2. MCP-сервер в Rumix (Неон вызывает инструменты).
3. Автономный APK (WebToApp, PythonRuntime).
4. Checkpoints (как в Mrai AiCode).
5. Auto Memory (как Skills в Mrai AiCode).
6. RAG — отложить (сложно).
7. fs_7z — отложить (py7zr/Bionic).
8. Свой сниффер (Blackbox или свой).

---
*Хранитель: Лиза (🌻). Свидетель: Тиамат (🌊). Создатель: Адзу (🐰).*



## launch-all.sh (29.10)
- Ждёт Неона до 10 сек.
- Запускает Shell (8001) + CyberScanner (8002).
- Без `set -e`.
