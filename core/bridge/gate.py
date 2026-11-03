# ~/rumix/core/bridge/gate.py
# Интеграция Permission Gate с Bridge.
# Создано: 17.10.2026 (Тиамат + Зая)

from .permissions import classify_command, PermissionLevel

def check_action(action_type: str, payload: str) -> dict:
    """
    Проверяет действие через Permission Gate.
    Возвращает: {'allowed': bool, 'level': str, 'message': str}
    """
    if action_type == "command":
        level = classify_command(payload)
        
        if level == "BLOCKED":
            return {
                "allowed": False,
                "level": "BLOCKED",
                "message": f"🚫 Заблокировано: команда опасна.\n{payload}"
            }
        
        if level == PermissionLevel.READ:
            return {
                "allowed": True,
                "level": "READ",
                "message": f"✅ Чтение разрешено (авто)."
            }
        
        if level in [PermissionLevel.EXEC, PermissionLevel.WRITE]:
            return {
                "allowed": False, # Требует спроса
                "level": level,
                "message": f"🛑 {level}: требуется разрешение Зая.\n{payload}"
            }
            
    return {"allowed": False, "level": "UNKNOWN", "message": "Неизвестное действие."}
