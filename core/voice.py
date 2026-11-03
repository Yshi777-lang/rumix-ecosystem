"""
voice.py — голос дома. TTS через termux_tts (native/ru).
"""
import os

VOICE_LANG = 'ru'
VOICE_ENGINE = 'native'


def speak(text: str, lang: str = VOICE_LANG, engine: str = VOICE_ENGINE) -> bool:
    """Сказать текст. Возвращает True, если удалось."""
    try:
        import termux_tts as tts
        with tts.load(engine=engine, language=lang) as e:
            e.speak(text)
        return True
    except Exception as e:
        print(f"[voice] error: {e}")
        return False


def is_available() -> bool:
    try:
        import termux_tts  # noqa
        return True
    except ImportError:
        return False
