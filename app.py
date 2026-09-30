"""GenAI-Portfolio hub: serves all six demos from one process.

    /p1  image captioning      (Gradio)
    /p2  web chatbot           (Flask)
    /p3  voice assistant       (Flask)
    /p4  meeting assistant     (Gradio)
    /p5  PDF data chatbot      (Flask)
    /p6  babel fish translator (Flask)

Run locally:  uvicorn app:app --port 7860
"""
import os
import time
from collections import defaultdict, deque

import gradio as gr
from a2wsgi import WSGIMiddleware
from fastapi import FastAPI
from flask import Flask, jsonify, request

import config  # noqa: F401  (loads .env)
from projects.p1_image_captioning.routes import iface as p1_demo
from projects.p2_web_chatbot.routes import bp as p2
from projects.p3_voice_assistant.server import bp as p3
from projects.p4_meeting_assistant.app_interface import demo as p4_demo
from projects.p5_data_chatbot.server import bp as p5
from projects.p6_babel_fish.server import bp as p6

SITE_URL = os.environ.get("SITE_URL", "")  # the Vercel landing page, if deployed

# --- Flask side (p2, p3, p5, p6) -------------------------------------------------
flask_app = Flask(__name__)
flask_app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(32)
flask_app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024  # uploads / recordings

for prefix, bp in (("/p2", p2), ("/p3", p3), ("/p5", p5), ("/p6", p6)):
    flask_app.register_blueprint(bp, url_prefix=prefix)

# Every POST can spend Groq quota or CPU, so cap it per visitor.
RATE_LIMIT, RATE_WINDOW = 40, 600  # requests per seconds
_hits = defaultdict(deque)


@flask_app.before_request
def rate_limit():
    if request.method != "POST":
        return None
    ip = (request.headers.get("X-Forwarded-For") or request.remote_addr or "?").split(",")[0].strip()
    now, hits = time.time(), _hits[ip]
    while hits and now - hits[0] > RATE_WINDOW:
        hits.popleft()
    if len(hits) >= RATE_LIMIT:
        return jsonify({"error": "Too many requests, please slow down."}), 429
    hits.append(now)
    return None


@flask_app.route("/")
def hub():
    links = "".join(
        f'<li><a href="/{k}/">{k.upper()} &mdash; {t}</a></li>'
        for k, t in (("p1", "Image captioning"), ("p2", "Web chatbot"), ("p3", "Voice assistant"),
                     ("p4", "Meeting assistant"), ("p5", "PDF data chatbot"), ("p6", "Babel Fish"))
    )
    back = f'<p><a href="{SITE_URL}">&larr; Back to GenAI-Portfolio</a></p>' if SITE_URL else ""
    return (f"<!doctype html><title>GenAI-Portfolio demos</title>"
            f"<body style='font:18px system-ui;background:#0D0D1A;color:#fff;padding:2rem'>"
            f"<h1>GenAI-Portfolio demos</h1><ul>{links}</ul>{back}</body>")


# --- ASGI root: Gradio apps mounted first, Flask catches everything else ----------
app = FastAPI(title="GenAI-Portfolio")
app = gr.mount_gradio_app(app, p1_demo, path="/p1")
app = gr.mount_gradio_app(app, p4_demo, path="/p4")
app.mount("/", WSGIMiddleware(flask_app))
