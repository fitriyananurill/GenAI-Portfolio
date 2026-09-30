from groq_client import chat_messages

SYSTEM = (
    "You are a friendly, curious chat companion. Keep replies to one to three short sentences, "
    "match the user's language, and ask a light follow-up question when it feels natural."
)
MAX_TURNS = 6


def generate_response(user_input, history):
    """history: list of {"role": "user"|"assistant", "content": str} kept by the browser."""
    turns = [
        {"role": m["role"], "content": str(m.get("content", ""))[:1000]}
        for m in history[-MAX_TURNS:]
        if isinstance(m, dict) and m.get("role") in ("user", "assistant")
    ]
    messages = [{"role": "system", "content": SYSTEM}, *turns, {"role": "user", "content": user_input}]
    return chat_messages(messages, max_tokens=300)
