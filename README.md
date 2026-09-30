# GenAI-Portfolio

Six small generative-AI projects behind one domain. Everything runs on hosted APIs (Groq), so the whole site deploys to Vercel's free tier.

| # | Project | What it does | Stack |
|---|---------|--------------|-------|
| p1 | Image captioning | Describes an uploaded photo | Flask, Groq vision (Qwen) |
| p2 | Web chatbot | Small talk with short memory | Flask, Groq (gpt-oss) |
| p3 | Voice assistant | Speak, hear the answer | Flask, Groq (Whisper + gpt-oss), gTTS |
| p4 | Meeting assistant | Transcript + summary of a recording | Flask, Groq (Whisper + gpt-oss) |
| p5 | PDF data chatbot | Ask questions about a PDF | Flask, BM25 retrieval, Groq, pypdf |
| p6 | Babel Fish | Speak English, hear it translated | Flask, Groq, gTTS |

## Layout

```
web/              static landing page + shared demo CSS (served by Flask)
app.py            Flask app (Vercel runs it directly): mounts p1-p6 under /p1 ... /p6, rate limit, errors
config.py         loads .env
groq_client.py    shared Groq REST client (chat, vision, transcription)
projects/         the six projects (one Flask blueprint each)
vercel.json       empty on purpose: Vercel auto-detects Flask from app.py
```

## Run locally

```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
echo GROQ_API_KEY=your_key > .env
python app.py                  # http://127.0.0.1:8000
```

## Deploy to Vercel (free)

1. Push this repo to GitHub.
2. On vercel.com: **Add New -> Project**, import the repo. Leave Framework Preset on "Other" / auto-detected and leave Root Directory as the repo root. No build command.
3. **Settings -> Environment Variables**: add `GROQ_API_KEY`. Redeploy.
4. **Settings -> Domains** to attach your own domain.

Edit `web/config.js` for your name and social links.

## Limits worth knowing

- Uploads are capped at 4 MB (Vercel's request limit is 4.5 MB). Images are shrunk in the browser first.
- Vercel limits how long a function may run (depends on your plan). Long recordings in p4 may not finish.
- Serverless keeps no state, so p2 and p5 keep chat history and PDF text in the browser and send them with each request.
- Rate limiting is in memory, per server instance: enough to stop one client hammering the demo, not a hard guarantee. Watch your Groq usage.
