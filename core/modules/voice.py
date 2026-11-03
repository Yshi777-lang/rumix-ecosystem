"""voice.py — настройки и запуск TTS."""
from core.modules import module, ModuleResult
from core import voice as core_voice

m = module("voice", "Голос", "🗣️", "Настройки TTS и готовность голоса (core/voice.py).")

_config = {
    "engine": "native",
    "lang": "ru"
}

@m.get
def state():
    """Возвращает текущие настройки и доступность."""
    available = core_voice.is_available()
    return ModuleResult(
        data={
            "config": _config,
            "tts_available": available,
            "limitations": [] if available else ["termux-tts не установлен: pip install termux-tts"]
        },
        confidence="high" if available else "none"
    )

@m.post
def action(data):
    """Либо озвучивает текст, либо меняет настройки."""
    # 1. Если просят изменить настройки (set)
    if "set" in data:
        new_cfg = data["set"]
        allowed_engines = ["native"]
        allowed_langs = ["ru", "en", "de", "fr"]
        
        if "engine" in new_cfg and new_cfg["engine"] not in allowed_engines:
            return ModuleResult({"error": f"Неизвестный движок. Доступны: {allowed_engines}"}, code=400)
        if "lang" in new_cfg and new_cfg["lang"] not in allowed_langs:
            return ModuleResult({"error": f"Неизвестный язык. Доступны: {allowed_langs}"}, code=400)

        _config.update(new_cfg)
        return ModuleResult({"config": _config})

    # 2. Если просят озвучить текст (text)
    if "text" in data:
        text = data["text"].strip()
        if not text:
            return ModuleResult({"error": "Пустой текст"}, code=400)
        
        success = core_voice.speak(text, lang=_config["lang"], engine=_config["engine"])
        
        if success:
            return ModuleResult({"said": True, "text": text})
        else:
            return ModuleResult({"said": False, "error": "Ошибка озвучки"}, status="error", code=500)

    return ModuleResult({"error": "Нужен 'set' (настройки) или 'text' (озвучка)"}, code=400)
