# Hugging Face Spaces (Docker SDK) image for the GenAI-Portfolio demos.
FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Spaces runs containers as uid 1000.
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONUNBUFFERED=1
WORKDIR /home/user/app

COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Bake the models into the image so the first visitor doesn't wait for downloads.
RUN python -c "from transformers import AutoModel, AutoTokenizer, AutoModelForSeq2SeqLM, BlipForConditionalGeneration, BlipProcessor; \
BlipProcessor.from_pretrained('Salesforce/blip-image-captioning-base'); BlipForConditionalGeneration.from_pretrained('Salesforce/blip-image-captioning-base'); \
AutoTokenizer.from_pretrained('facebook/blenderbot-400M-distill'); AutoModelForSeq2SeqLM.from_pretrained('facebook/blenderbot-400M-distill'); \
AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2'); AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')"

COPY --chown=user . .

EXPOSE 7860
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860", "--proxy-headers", "--forwarded-allow-ips=*"]
