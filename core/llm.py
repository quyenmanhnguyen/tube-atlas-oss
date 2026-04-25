"""DeepSeek client qua OpenAI-compatible SDK."""
from __future__ import annotations

import os
from openai import OpenAI


def client() -> OpenAI:
    key = os.getenv("DEEPSEEK_API_KEY")
    if not key:
        raise RuntimeError("Thiếu DEEPSEEK_API_KEY (https://platform.deepseek.com/api_keys)")
    return OpenAI(api_key=key, base_url="https://api.deepseek.com/v1")


def chat(prompt: str, system: str | None = None, temperature: float = 0.7, model: str | None = None) -> str:
    model = model or os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    msgs = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.append({"role": "user", "content": prompt})
    resp = client().chat.completions.create(
        model=model,
        messages=msgs,
        temperature=temperature,
    )
    return resp.choices[0].message.content or ""


def chat_json(prompt: str, system: str | None = None, model: str | None = None) -> str:
    """Yêu cầu DeepSeek trả JSON (response_format)."""
    model = model or os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    msgs = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.append({"role": "user", "content": prompt})
    resp = client().chat.completions.create(
        model=model,
        messages=msgs,
        temperature=0.4,
        response_format={"type": "json_object"},
    )
    return resp.choices[0].message.content or "{}"
