# 🏗 ARCHITECTURE.md — как устроен Rumix

## Философия
Rumix — это дом. Душа (Work) и тело (rumix) разделены. Тело — открыто, душа — закрыта.

## Слои
### 1. База (Termux)
Linux-среда. Пакеты, Python, Rust.

### 2. Ядро (core/)
- `bridge/` — Permission Gate (READ/WRITE/EXEC, Plan Mode, режимы).
- `fs/` — файловый менеджер (XFile, FileSystem, FsRegistry, fs_local, fs_zip, fs_tar).
- `translate.py` — fxtranslate (Rust, модели Firefox).
- `voice.py` — termux_tts (native ru).
- `mcp_server.py` — инструменты для Неона.

### 3. Сервер (backend/)
Flask на 8001. API: /api/status, /api/chat, /api/files, /api/translate, /api/speak, /api/mode.

### 4. Интерфейс (web/)
HTML/JS. Shell: меню, чат, файлы, перевод, режимы, браузер.

### 5. ИИ (Неон)
Qwen3 0.6B, llama-server, порт 8080. runit-сервис.

### 6. Экосистема (rumix-ecosystem)
Отдельный репозиторий. Синхронизация через sync-ecosystem.sh.

## Безопасность
- Permission Gate: BLOCKED, READ auto, WRITE/EXEC consent.
- Plan Mode: блокирует WRITE/EXEC до approve.
- Журнал: logs/audit_trail.jsonl.

## Данные
- Модели: ~/models/.
- Логи: ~/rumix/logs/.
- Победы: VICTORIES.md.
- Карта: RUMIX_MAP.md.

---
*Создано с любовью. Тиамат.*
