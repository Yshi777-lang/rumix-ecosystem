"""stt.py — запись с микрофона → whisper.cpp. Проверено по исходникам API."""
import os
import shutil
import subprocess
import time
from pathlib import Path

from core.modules import module, ModuleResult

m = module("stt", "Голосовой ввод", "🎙️",
           "Запись + распознавание речи (whisper.cpp). POST {seconds, lang}.")

MODEL = os.environ.get("RUMIX_WHISPER_MODEL",
                       os.path.expanduser("~/rumix/models/ggml-base.bin"))
TMP = Path.home() / "rumix" / "tmp"


def _bin(*names):
    return next((p for n in names if (p := shutil.which(n))), None)


def _missing():
    """Чего не хватает. Каждый пункт — с командой установки."""
    miss = []
    if not _bin("termux-microphone-record"):
        miss.append("pkg install termux-api + приложение Termux:API (F-Droid)")
    if not _bin("whisper-cli", "whisper"):
        miss.append("whisper.cpp: собрать cmake → whisper-cli в $PREFIX/bin")
    if not _bin("ffmpeg"):
        miss.append("pkg install ffmpeg (рекордер даёт .m4a, whisper читает wav)")
    if not os.path.exists(MODEL):
        miss.append(f"модель ggml-base.bin → {MODEL} (или env RUMIX_WHISPER_MODEL)")
    return miss


def _record(seconds):
    """Запись. -l в СЕКУНДАХ (CLI сам умножает на 1000), -q финализирует файл."""
    TMP.mkdir(parents=True, exist_ok=True)
    rec = TMP / f"stt-{int(time.time())}.m4a"
    if rec.exists():
        rec.unlink()

    r = subprocess.run([_bin("termux-microphone-record"), "-f", str(rec),
                        "-l", str(seconds)],
                       capture_output=True, text=True, timeout=10)
    out = (r.stdout + r.stderr).strip()
    if "Recording started" not in out:
        raise RuntimeError(out or "рекордер не ответил")

    # Запись идёт в сервисе Termux:API, команда вернулась сразу.
    # Ждём лимит и глушим: без -q файл может остаться нефинализированным.
    time.sleep(seconds + 1)
    subprocess.run([_bin("termux-microphone-record"), "-q"],
                   capture_output=True, text=True, timeout=10)

    if not rec.exists() or rec.stat().st_size == 0:
        raise RuntimeError("файл записи пуст (микрофон занят?)")
    return rec


def _to_wav(src):
    """m4a/aac → 16 кГц моно wav. whisper-cli m4a не читает."""
    wav = src.with_suffix(".wav")
    r = subprocess.run([_bin("ffmpeg"), "-y", "-i", str(src), "-ar", "16000",
                        "-ac", "1", "-c:a", "pcm_s16le", str(wav)],
                       capture_output=True, text=True, timeout=120)
    if r.returncode != 0 or not wav.exists():
        raise RuntimeError(f"ffmpeg: {r.stderr.strip()[-200:]}")
    return wav


@m.get
def state():
    """Готовность: рекордер, whisper.cpp, ffmpeg, модель."""
    miss = _missing()
    return ModuleResult({"ready": not miss, "missing": miss, "model": MODEL},
                        status="full" if not miss else "unavailable",
                        confidence="high" if not miss else "low",
                        limitations=miss)


@m.post
def action(data):
    """POST {"seconds": 1..30, "lang": "ru"} — записать и распознать."""
    miss = _missing()
    if miss:
        return ModuleResult({"missing": miss}, status="unavailable",
                            confidence="high", limitations=miss, code=503)

    try:
        seconds = max(1, min(int(data.get("seconds", 5)), 30))
    except (TypeError, ValueError):
        return ModuleResult({"error": "seconds — целое 1..30"},
                            status="partial", code=400)

    lang = str(data.get("lang", "ru")).strip() or "ru"
    rec = wav = None
    try:
        rec = _record(seconds)
        wav = _to_wav(rec)
        # -l обязателен: дефолт whisper-cli — английский, русская речь станет мусором
        r = subprocess.run([_bin("whisper-cli", "whisper"), "-m", MODEL,
                            "-f", str(wav), "-l", lang, "-nt", "-np"],
                           capture_output=True, text=True, timeout=240)
        if r.returncode != 0:
            return ModuleResult({"error": f"whisper: {r.stderr.strip()[-200:]}"},
                                status="error", code=500)
        text = " ".join(r.stdout.split())
        if not text:
            return ModuleResult({"text": ""}, status="partial", confidence="low",
                                limitations=["тишина в записи или модель мала"],
                                raw_ref=str(wav))
        return ModuleResult({"text": text, "seconds": seconds, "lang": lang,
                             "wav": str(wav)}, raw_ref=str(wav))
    except subprocess.TimeoutExpired:
        return ModuleResult({"error": "таймаут записи/распознавания"},
                            status="error", code=504)
    except Exception as e:
        return ModuleResult({"error": str(e)}, status="error", code=500)
    finally:
        for p in (rec, wav):
            try:
                if p and Path(p).exists():
                    Path(p).unlink()
            except OSError:
                pass
