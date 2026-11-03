#!/data/data/com.termux/files/usr/bin/env python3
"""
local_provider.py — LocalProvider v0.1.

Обёртка над api.py (llama-server).
Runtime не знает про localhost:8080, llama-server, Qwen3.

LocalProvider — это адаптер.
"""

from runtime.provider import ModelProvider, ModelRequest, ModelResponse
from runtime import api


class LocalProvider(ModelProvider):
    name = "local"
    model = "qwen3-0.6b-q4"

    def generate(self, request):
        """Вызвать llama-server через api.ask()."""
        data = api.ask(
            messages=request.messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            timeout=request.timeout,
            return_usage=True,
        )
        return ModelResponse(
            text=data.get("content", ""),
            provider=self.name,
            model=self.model,
            usage=data.get("usage", {}),
            timings=data.get("timings", {}),
        )

    def health(self):
        """Проверить, жив ли llama-server."""
        return api.health()


if __name__ == "__main__":
    p = LocalProvider()
    print(f"LocalProvider: {p.name} / {p.model}")
    print(f"health: {p.health()}")

    if p.health():
        req = ModelRequest(
            messages=[{"role": "user", "content": "Скажи одно слово: привет"}],
            max_tokens=30,
        )
        resp = p.generate(req)
        print(f"Ответ: {resp}")
        print(f"Текст: {resp.text}")
