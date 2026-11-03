# test_harness.py — минимальный тест харнеса с Неоном
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from harness.llm import OpenAICompatLLM
from harness.loop import run_agent
from harness.tools import tool

# Наш Неон (OpenAI-совместимый API)
llm = OpenAICompatLLM(
    model="qwen2.5-1.5b-instruct-q4_k_m",
    api_key="",
    base_url="http://127.0.0.1:8080/v1"
)

@tool("Сложить два числа. Используй для ЛЮБЫХ вычислений", params={"a": "первое число", "b": "второе число"})
def add(a: float, b: float) -> float:
    return a + b

print("=== Тест 1: простой вопрос ===")
result = run_agent(
    llm=llm,
    tools=[add],
    system="Ты — калькулятор. Отвечай кратко.",
    messages=[{"role": "user", "content": "Сколько будет 2 + 3?"}],
    max_steps=3
)
print(f"Ответ: {result.text}")
print(f"Шагов: {result.steps}")
print(f"Токенов: {result.usage.input_tokens} in, {result.usage.output_tokens} out")
