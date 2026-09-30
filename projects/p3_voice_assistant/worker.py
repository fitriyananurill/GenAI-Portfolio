from io import BytesIO
from gtts import gTTS
from langdetect import detect

from groq_client import transcribe, chat


def speech_to_text(audio_binary):
    return transcribe(BytesIO(audio_binary), "audio.wav", "audio/wav", timeout=60)


def openai_process_message(user_message):
    prompt = "Act like a personal assistant. You can respond to questions, translate sentences, summarize news, and give recommendations. Keep responses concise - 2 to 3 sentences maximum."
    return chat(prompt, user_message)


def text_to_speech(text):
    """Return MP3 bytes. Kept in memory so concurrent visitors never share a file."""
    try:
        detected_lang = detect(text)
    except Exception:
        detected_lang = "en"

    lang = "id" if detected_lang == "id" else "en"
    buffer = BytesIO()
    gTTS(text=text, lang=lang).write_to_fp(buffer)
    return buffer.getvalue()
