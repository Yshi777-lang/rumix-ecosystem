#!/data/data/com.termux/files/usr/bin/env python3
"""
provider.py — ModelProvider v0.1.

Runtime не должен знать, какая LLM под капотом.
Provider отвечает за способ доступа к модели.
Модель отвечает за сам inference.

Минимальный контракт:
- ModelRequest  — запрос
- ModelResponse — ответ
- ModelProvider — базовый класс

Provider не равно Model.
"""


from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class ModelRequest:
    messages: list
    max_tokens: int = 400
    temperature: float = 0.2
    timeout: int = 900

    def to_dict(self):
        return {
            "messages": self.messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "timeout": self.timeout,
        }


@dataclass
class ModelResponse:
    text: str
    provider: str = "unknown"
    model: str = "unknown"
    usage: dict = field(default_factory=dict)
    timings: dict = field(default_factory=dict)

    def to_dict(self):
        return {
            "text": self.text,
            "provider": self.provider,
            "model": self.model,
            "usage": self.usage,
            "timings": self.timings,
        }

    def __repr__(self):
        return f"ModelResponse(provider={self.provider}, len={len(self.text)})"


class ModelProvider:
    name = "base"
    model = "unknown"

    def generate(self, request):
        raise NotImplementedError("Provider must implement generate()")
