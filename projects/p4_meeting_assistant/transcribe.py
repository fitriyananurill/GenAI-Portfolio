from groq_client import transcribe


def transcribe_audio(file_obj, filename, mime="audio/mpeg"):
    return transcribe(file_obj, filename, mime)
