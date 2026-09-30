from functools import lru_cache


@lru_cache(maxsize=1)
def _load():
    # Loaded on first request so the hub app starts fast and idle demos cost no RAM.
    from transformers import BlipProcessor, BlipForConditionalGeneration

    name = "Salesforce/blip-image-captioning-base"
    return BlipProcessor.from_pretrained(name), BlipForConditionalGeneration.from_pretrained(name)


def generate_caption(image):
    """Take a PIL Image, return the BLIP caption."""
    if image is None:
        return "Upload a picture first."
    try:
        processor, model = _load()
        inputs = processor(images=image, return_tensors="pt")
        outputs = model.generate(**inputs)
        return processor.decode(outputs[0], skip_special_tokens=True)
    except Exception as e:
        return f"Terjadi kesalahan: {e}"
