"""
mcp_server.py — MCP-сервер для Rumix.
Даёт инструменты (read_file, translate, speak) внешним LLM (и Неону).
"""

from typing import Dict, Any
import os


class McpServer:
    """Простой MCP-сервер: инструменты + вызов."""

    def __init__(self):
        self.tools = {
            "read_file": self._read_file,
            "translate": self._translate,
            "speak": self._speak,
        }

    def list_tools(self) -> Dict[str, Any]:
        """Список инструментов (для MCP)."""
        return {
            "tools": [
                {"name": "read_file", "description": "Прочитать файл", "input": {"path": "string"}},
                {"name": "translate", "description": "Перевести текст", "input": {"text": "string", "src": "string", "trg": "string"}},
                {"name": "speak", "description": "Озвучить текст", "input": {"text": "string"}},
            ]
        }

    def call(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Вызвать инструмент."""
        if name not in self.tools:
            return {"error": f"Unknown tool: {name}"}
        try:
            result = self.tools[name](**args)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}

    def _read_file(self, path: str) -> str:
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()[:4000]

    def _translate(self, text: str, src: str = "en", trg: str = "ru") -> str:
        from .translate import translate
        return translate(text, src, trg)

    def _speak(self, text: str) -> str:
        from .voice import speak
        return "ok" if speak(text) else "error"
