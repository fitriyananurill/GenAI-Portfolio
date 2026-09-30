"""Shared Groq REST client for all projects.

Plain REST calls instead of the openai SDK: its jiter dependency is a native
.pyd that Windows Smart App Control blocks, and it keeps the Vercel bundle small.
"""
import os
import httpx
from config import GROQ_API_KEY

BASE_URL = "https://api.groq.com/openai/v1"
CHAT_MODEL = "openai/gpt-oss-120b"
VISION_MODEL = "qwen/qwen3.8-27b"


def _headers():
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not set. Add it to .env (local) or the Vercel project settings.")
    return {"Authorization": f"Bearer {GROQ_API_KEY}"}


def transcribe(file_obj, filename, mime="audio/mpeg", model="whisper-large-v3", timeout=50):
    response = httpx.post(
        f"{BASE_URL}/audio/transcriptions",
        headers=_headers(),
        data={"model": model},
        files={"file": (os.path.basename(filename), file_obj, mime)},
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()["text"]


def chat_messages(messages, model=CHAT_MODEL, max_tokens=1000, timeout=50):
    """Chat completion over a full message list; returns the reply text."""
    payload = {"model": model, "messages": messages, "max_tokens": max_tokens}
    # Reasoning models would otherwise spend the token budget thinking.
    if model.startswith("openai/gpt-oss"):
        payload["reasoning_effort"] = "low"
    elif model.startswith("qwen/"):
        payload["reasoning_effort"] = "none"
    response = httpx.post(f"{BASE_URL}/chat/completions", headers=_headers(), json=payload, timeout=timeout)
    response.raise_for_status()
    return (response.json()["choices"][0]["message"]["content"] or "").strip()


def chat(system_prompt, user_message, model=CHAT_MODEL, max_tokens=1000, timeout=50):
    return chat_messages(
        [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}],
        model=model, max_tokens=max_tokens, timeout=timeout,
    )
