"""Shared Groq REST client for all projects.

Plain REST calls instead of the openai SDK: its jiter dependency is a native
.pyd that Windows Smart App Control blocks.
"""
import os
import httpx
from config import GROQ_API_KEY

BASE_URL = "https://api.groq.com/openai/v1"


def _headers():
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not set. Add it to .env in the repo root.")
    return {"Authorization": f"Bearer {GROQ_API_KEY}"}


def transcribe(file_obj, filename, mime="audio/mpeg", model="whisper-large-v3", timeout=120):
    response = httpx.post(
        f"{BASE_URL}/audio/transcriptions",
        headers=_headers(),
        data={"model": model},
        files={"file": (os.path.basename(filename), file_obj, mime)},
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()["text"]


def chat(system_prompt, user_message, model="openai/gpt-oss-120b", max_tokens=1000, timeout=60):
    response = httpx.post(
        f"{BASE_URL}/chat/completions",
        headers=_headers(),
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "max_tokens": max_tokens,
        },
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]
