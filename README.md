---
title: GenAI-Portfolio
emoji: 🚀
colorFrom: pink
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# GenAI-Portfolio

Six small generative-AI projects, one repo.

| # | Project | Stack |
|---|---------|-------|
| p1 | Image captioning | Gradio, BLIP |
| p2 | Web chatbot | Flask, BlenderBot |
| p3 | Voice assistant | Flask, Groq (Whisper + gpt-oss), gTTS |
| p4 | Meeting assistant | Gradio, Groq (Whisper + gpt-oss) |
| p5 | PDF data chatbot | LangChain, Chroma, MiniLM, Groq |
| p6 | Babel Fish translator | Flask, Groq, gTTS |

## Layout

```
app.py            hub app: serves p1-p6 under /p1 ... /p6 (uvicorn app:app)
config.py         loads .env
groq_client.py    shared Groq REST client
projects/         the six projects
site/             static landing page (deployed to Vercel)
Dockerfile        demos image (deployed to Hugging Face Spaces)
```

## Run locally

```bash
python -m venv venv && venv\Scripts\activate     # Windows
pip install -r requirements.txt
echo GROQ_API_KEY=your_key > .env
uvicorn app:app --port 7860                      # http://127.0.0.1:7860
```

## Deploy (both free)

**Demos -> Hugging Face Spaces** (Docker, CPU Basic: 2 vCPU / 16 GB)
1. Create a Space at huggingface.co/new-space, SDK **Docker**.
2. Add a Space secret `GROQ_API_KEY` (and optionally `SITE_URL` = your Vercel URL).
3. Push this repo to the Space's git remote. It builds from `Dockerfile`.

**Landing page -> Vercel**
1. Put your Space URL into `site/config.js` (`SPACE_URL`), plus your name and links.
2. Import the repo on vercel.com and set **Root Directory** to `site`. No build step.
3. Add your domain under Project -> Settings -> Domains.
