from functools import lru_cache

MODEL_NAME = "facebook/blenderbot-400M-distill"


@lru_cache(maxsize=1)
def _load():
    # Loaded on first request so the hub app starts fast and idle demos cost no RAM.
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

    return AutoTokenizer.from_pretrained(MODEL_NAME), AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)


def generate_response(user_input, conversation_history):
    tokenizer, model = _load()
    conversation_history = conversation_history[-6:]
    history_string = "\n".join(conversation_history)
    prompt = history_string + f"\nUser: {user_input}\nBot:"
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
    outputs = model.generate(
        **inputs,
        max_new_tokens=60,
        no_repeat_ngram_size=3,
        repetition_penalty=1.3,
        do_sample=True,
        temperature=0.6,
        top_p=0.85,
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
    conversation_history.append(f"User: {user_input}")
    conversation_history.append(f"Bot: {response}")
    return response, conversation_history
