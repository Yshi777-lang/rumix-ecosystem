# ~/rumix/core/bridge/file_gate.py
# Врата для файловых операций.
# Создано: 17.10.2026 (Тиамат + Зая)

from .permissions import check_file_access

def check_file(path: str, mode: str = "read") -> dict:
    """
    Проверяет доступ к файлу.
    mode: "read" (авто, если не секрет), "write" (нужно согласие)
    """
    # 1. Проверка на секреты и системные файлы
    if not check_file_access(path, mode):
        return {
            "allowed": False,
            "level": "BLOCKED",
            "message": f"🚫 Доступ к файлу запрещён (секрет или системный): {path}"
        }
    
    # 2. Чтение разрешено, если это не секрет
    if mode == "read":
        return {
            "allowed": True,
            "level": "READ",
            "message": f"✅ Чтение файла разрешено: {path}"
        }
        
    # 3. Запись всегда требует согласия
    if mode == "write":
        return {
            "allowed": False,
            "level": "WRITE",
            "message": f"🛑 Запись в файл требует разрешения Зая: {path}"
        }
    
    return {"allowed": False, "level": "UNKNOWN", "message": "Неизвестный режим."}
