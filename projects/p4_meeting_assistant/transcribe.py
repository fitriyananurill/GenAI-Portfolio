from groq_client import transcribe


def transcribe_audio(audio_path):
    with open(audio_path, "rb") as f:
        return transcribe(f, audio_path, "audio/mpeg")
