#!/data/data/com.termux/files/usr/bin/env python3
"""
sanitizer.py — фильтр секретов в логах и данных.
Принцип: raw logs -> sanitizer -> structured result -> Qwen.
Не отправлять модели: tokens, passwords, API keys, cookies,
private paths, personal data.
"""

import re

PATTERNS = [
    # Токены GitHub (все виды)
    (re.compile(r'(ghp_|gho_|ghu_|ghs_|ghr_|github_pat_)[A-Za-z0-9_]{20,}'), '[GITHUB_TOKEN]'),
    # API ключи OpenAI / Anthropic / DeepSeek / generic sk-
    (re.compile(r'sk-ant-[A-Za-z0-9_\-]{20,}'), '[ANTHROPIC_KEY]'),
    (re.compile(r'sk-proj-[A-Za-z0-9_\-]{20,}'), '[OPENAI_PROJECT_KEY]'),
    (re.compile(r'sk-[A-Za-z0-9_\-]{20,}'), '[API_KEY]'),
    # HuggingFace
    (re.compile(r'hf_[A-Za-z0-9]{20,}'), '[HF_TOKEN]'),
    # Google API
    (re.compile(r'AIza[A-Za-z0-9_\-]{30,}'), '[GOOGLE_API_KEY]'),
    # Slack
    (re.compile(r'xox[baprs]-[A-Za-z0-9\-]{10,}'), '[SLACK_TOKEN]'),
    # AWS
    (re.compile(r'AKIA[A-Z0-9]{16}'), '[AWS_ACCESS_KEY]'),
    # Twilio
    (re.compile(r'SK[0-9a-fA-F]{32}'), '[TWILIO_KEY]'),
    # JWT с Bearer
    (re.compile(r'Bearer\s+eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}'), 'Bearer [JWT]'),
    # JWT без Bearer
    (re.compile(r'eyJ[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{20,}'), '[JWT]'),
    # Пароли и ключи
    (re.compile(r'(?i)(password|passwd|pwd|secret|token|api[_-]?key|access[_-]?key|auth[_-]?token)\s*[=:]\s*\S+'), r'\1=[REDACTED]'),
    # Cookies
    (re.compile(r'(?i)(cookie|set-cookie)\s*:\s*\S+'), 'cookie=[REDACTED]'),
    # Приватные пути
    (re.compile(r'/data/data/com\.termux/files/home/[^\s"\']+'), '[HOME_PATH]'),
    (re.compile(r'/storage/emulated/0/[^\s"\']+'), '[STORAGE_PATH]'),
    # Домашние IP (RFC1918)
    (re.compile(r'\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2[0-9]|3[01])\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3})\b'), '[LAN_IP]'),
]


def sanitize(text):
    """Очистить текст от секретов."""
    if not isinstance(text, str):
        return text
    result = text
    for pattern, replacement in PATTERNS:
        result = pattern.sub(replacement, result)
    return result


def sanitize_dict(data):
    """Рекурсивно очистить словарь/список."""
    if isinstance(data, dict):
        return {k: sanitize_dict(v) for k, v in data.items()}
    if isinstance(data, list):
        return [sanitize_dict(v) for v in data]
    if isinstance(data, str):
        return sanitize(data)
    return data


if __name__ == "__main__":
    tests = [
        "token: ghp_abcdefghij1234567890abcdefghij",
        "api_key=xyz12345",
        "password=secret123",
        "/data/data/com.termux/files/home/.zshrc",
        "192.168.1.100",
    ]
    for t in tests:
        print(f"BEFORE: {t}")
        print(f"AFTER:  {sanitize(t)}")
        print()
