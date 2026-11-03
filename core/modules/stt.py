"""stt.py — запись с микрофона и распознавание речи (whisper.cpp)."""
import os
import subprocess
import shutil
import tempfile
import time
from core.modules import module, ModuleResult

m = module("stt", "Голосовой ввод", "🎙️", "Готовность к распознаванию: рекордер, whisper.cpp, модель.")

DEFAULT_MODEL = os.path.expanduser("~/rumix/models/ggml-base.bin")
MODEL_PATH = os.environ.get("RUMIX_WHISPER_MODEL", DEFAULT_MODEL)

def _check_deps():
    """Проверяет наличие рекордера, whisper-cli и модели."""
    missing = []
    if not shutil.which("termux-microphone-record") is not None:
        missing.append("termux-microphone-record (pkg install termux-api)")
    if not shutil.which("whisper-cli") is not None:
        missing.append("whisper-cli (соберите whisper.cpp)")
    if not os.path.exists(MODEL_PATH):
        missing.append(f"модель whisper по пути {MODEL_PATH} (или задайте RUMIX_WHISPER_MODEL)")
    return missing

@m.get
def state():
    """Возвращает статус готовности."""
    missing = _check_deps()
    ready = len(missing) == 0
    return ModuleResult(
        data={
            "ready": ready,
            "missing": missing,
            "model": MODEL_PATH
        },
        status="ok" if ready else "unavailable",
        confidence="high" if ready else "none"
    )

@m.post
def action(data):
    """Запись и распознавание."""
    missing = _check_deps()
    if missing:
        return ModuleResult(
            data={"missing": missing},
            status="unavailable",
            confidence="none",
            code=503
        )

    seconds = int(data.get("seconds", 5))
    if seconds < 1 or seconds > 30:
        return ModuleResult({"error": "seconds должно быть от 1 до 30"}, code=400)

    wav_file = tempfile.mktemp(suffix=".wav")
    
    try:
        # 1. Запись
        subprocess.run(
            ["termux-microphone-record", "-f", wav_file, "-d", str(seconds)],
            capture_output=True, text=True, timeout=seconds + 5
        )
        
        # Ждём, пока файл появится (иногда termux-api пишет асинхронно)
        time.sleep(1)
        if not os.path.exists(wav_file):
            return ModuleResult({"error": "Файл записи не появился"}, status="error", code=500)

        # 2. Распознавание (whisper)
        # Таймаут 180 секунд (как советовал эксперт), чтобы не рвать долгую запись
        r = subprocess.run(
            ["whisper-cli", "-m", MODEL_PATH, "-f", wav_file, "-nt"],
            capture_output=True, text=True, timeout=180
        )
        
        if r.returncode != 0:
            return ModuleResult({"error": f"Whisper упал: {r.stderr}"}, status="error", code=500)
            
        text = r.stdout.strip()
        return ModuleResult({"text": text, "wav": wav_file})
        
    except subprocess.TimeoutExpired:
        return ModuleResult({"error": "Таймаут записи или распознавания"}, status="error", code=504)
    except Exception as e:
        return ModuleResult({"error": str(e)}, status="error", code=500)
