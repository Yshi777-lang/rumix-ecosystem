"""
translate.py — офлайн-перевод через fxtranslate (Rust CLI).
Модели Firefox Translations, без интернета после загрузки.
"""
import subprocess, shutil, os
from pathlib import Path

FXT = os.path.expanduser('~/.cargo/bin/fxtranslate')

def is_available() -> bool:
    return Path(FXT).exists()

def translate(text: str, src: str, trg: str, timeout: int = 60) -> str:
    if not is_available():
        raise RuntimeError('fxtranslate not installed')
    r = subprocess.run([FXT, 'translate', src, trg, text],
                       capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip() or 'fxtranslate failed')
    return r.stdout.strip()

def supported(lang: str) -> bool:
    try:
        r = subprocess.run([FXT, 'list', lang], capture_output=True, text=True, timeout=20)
        return r.returncode == 0 and 'languages' in r.stdout
    except Exception:
        return False
