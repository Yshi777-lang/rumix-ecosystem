#!/data/data/com.termux/files/usr/bin/env python3
"""
api.py — HTTP-клиент к llama-server.
Очистка <think>...</think> из ответа Qwen3.
"""

import json
import re
import requests

SERVER = "http://127.0.0.1:8080/v1/chat/completions"
MODELS_URL = "http://127.0.0.1:8080/v1/models"


def health():
    """Проверка: жив ли llama-server."""
    try:
        r = requests.get(MODELS_URL, timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def clean_think(text):
    """Убирает <think>...</think> из ответа Qwen3."""
    if not text:
        return text
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    text = re.sub(r"<think>.*$", "", text, flags=re.DOTALL)
    return text.strip()


def ask(messages, temperature=0.2, max_tokens=200, timeout=900,
        clean=True, return_usage=False):
    """Отправить messages в llama-server."""
    payload = {
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    response = requests.post(
        SERVER,
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"},
        timeout=timeout,
    )
    response.raise_for_status()

    data = response.json()
    content = data["choices"][0]["message"]["content"]

    if clean:
        content = clean_think(content)

    if return_usage:
        return {
            "content": content,
            "usage": data.get("usage", {}),
            "timings": data.get("timings", {}),
        }

    return content


if __name__ == "__main__":
    print("🔍 Проверка llama-server...")
    if not health():
        print("❌ llama-server не отвечает на 127.0.0.1:8080")
        exit(1)
    print("✅ llama-server жив")
    print()

    msgs = [{"role": "user", "content": "Скажи одно слово: привет"}]
    print("Отправляю запрос...")
    answer = ask(msgs, max_tokens=30)
    print(f"Ответ: {answer}")
