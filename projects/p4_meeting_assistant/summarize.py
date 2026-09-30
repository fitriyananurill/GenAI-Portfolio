from groq_client import chat


def summarize_transcript(transcript):
    if not transcript or not transcript.strip():
        return "Tidak ada teks untuk diringkas."

    prompt = (
        "You are an assistant that summarizes meeting transcripts. "
        "Read the transcript below and provide a concise summary highlighting "
        "the key points and any decisions or action items mentioned."
    )
    return chat(prompt, transcript)
