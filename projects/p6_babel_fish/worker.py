import os
from io import BytesIO
from dotenv import load_dotenv
import httpx
from gtts import gTTS

load_dotenv()

BASE_URL = "https://api.groq.com/openai/v1"


def _headers():
    return {"Authorization": f"Bearer {os.environ.get('GROQ_API_KEY')}"}

# Value dari dropdown "Choose a Voice" di frontend meniru format Watson,
# misal "es-LA_SofiaV3Voice". Prefix locale-nya (sebelum "_") sudah cukup
# untuk menentukan bahasa target terjemahan + kode bahasa gTTS.
VOICE_LANGUAGE_MAP = {
    "en-US": ("English", "en"),
    "en-GB": ("English", "en"),
    "fr-CA": ("French", "fr"),
    "fr-FR": ("French", "fr"),
    "it-IT": ("Italian", "it"),
    "pt-BR": ("Portuguese", "pt"),
    "es-ES": ("Spanish", "es"),
    "es-LA": ("Spanish", "es"),
}
DEFAULT_LANGUAGE = ("English", "en")


def get_target_language(voice):
    if not voice:
        return DEFAULT_LANGUAGE
    locale = voice.split("_")[0]
    return VOICE_LANGUAGE_MAP.get(locale, DEFAULT_LANGUAGE)


def speech_to_text(audio_binary):
    audio_file = BytesIO(audio_binary)
    audio_file.name = "audio.wav"

    response = httpx.post(
        f"{BASE_URL}/audio/transcriptions",
        headers=_headers(),
        data={"model": "whisper-large-v3"},
        files={"file": (audio_file.name, audio_file, "audio/wav")},
        timeout=60,
    )
    response.raise_for_status()
    text = response.json()["text"]
    print("recognised text:", text)
    return text


def watsonx_process_message(user_message, voice=""):
    language_name, _ = get_target_language(voice)

    prompt = f"""
    Translate the following English sentence into {language_name}.
    Reply ONLY with the translation, no explanations, no formatting, no extra text.

    English: {user_message}
    {language_name}:
    """

    response = httpx.post(
        f"{BASE_URL}/chat/completions",
        headers=_headers(),
        json={
            "model": "openai/gpt-oss-120b",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000,
            "reasoning_effort": "low",
            "temperature": 0,
        },
        timeout=60,
    )
    response.raise_for_status()
    response_text = response.json()["choices"][0]["message"]["content"]
    print("watsonx response:", response_text)
    return response_text.strip()


def text_to_speech(text, voice=""):
    _, lang_code = get_target_language(voice)

    try:
        tts = gTTS(text=text, lang=lang_code)
    except ValueError:
        tts = gTTS(text=text, lang="en")

    buffer = BytesIO()
    tts.write_to_fp(buffer)
    print("Text-to-Speech generated, lang:", lang_code)
    return buffer.getvalue()