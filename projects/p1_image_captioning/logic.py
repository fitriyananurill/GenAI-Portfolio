import base64

from groq_client import chat_messages, VISION_MODEL

ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}


def generate_caption(image_bytes, mime):
    """Describe an image in one sentence with a Groq vision model."""
    data_url = f"data:{mime};base64,{base64.b64encode(image_bytes).decode()}"
    return chat_messages(
        [{
            "role": "user",
            "content": [
                {"type": "text", "text": "Write a short, vivid caption for this image: one sentence, plain text, no preamble."},
                {"type": "image_url", "image_url": {"url": data_url}},
            ],
        }],
        model=VISION_MODEL,
        max_tokens=200,
    )
