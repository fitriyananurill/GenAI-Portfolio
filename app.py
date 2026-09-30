"""GenAI-Portfolio: all six demos in one Flask app.

    /p1  image captioning      /p4  meeting assistant
    /p2  web chatbot           /p5  PDF data chatbot
    /p3  voice assistant       /p6  Babel Fish translator

Static pages (landing, shared CSS) live in public/. On Vercel the CDN serves them
and api/index.py serves everything else; locally this app serves both.

Run locally:  python app.py   ->  http://127.0.0.1:8000
"""
import time
from collections import defaultdict, deque

import httpx
from flask import Flask, jsonify, request, send_from_directory

import config  # noqa: F401  (loads .env)
from projects.p1_image_captioning.routes import bp as p1
from projects.p2_web_chatbot.routes import bp as p2
from projects.p3_voice_assistant.server import bp as p3
from projects.p4_meeting_assistant.app_interface import bp as p4
from projects.p5_data_chatbot.server import bp as p5
from projects.p6_babel_fish.server import bp as p6

app = Flask(__name__, static_folder="public", static_url_path="")
# Vercel rejects request bodies above 4.5 MB; fail the same way locally.
app.config["MAX_CONTENT_LENGTH"] = 4 * 1024 * 1024

for prefix, bp in (("/p1", p1), ("/p2", p2), ("/p3", p3), ("/p4", p4), ("/p5", p5), ("/p6", p6)):
    app.register_blueprint(bp, url_prefix=prefix)

# Every POST spends free-tier API quota, so cap it per visitor. State is per server
# instance, which is enough to stop a single client hammering the demo.
RATE_LIMIT, RATE_WINDOW = 40, 600  # requests per seconds
_hits = defaultdict(deque)


@app.before_request
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


@app.route("/")
def landing():
    return send_from_directory(app.static_folder, "index.html")


@app.errorhandler(413)
def too_large(_):
    return jsonify({"error": "That file is too large (limit 4 MB)."}), 413


@app.errorhandler(httpx.HTTPStatusError)
def upstream_error(err):
    code = err.response.status_code
    msg = "The AI service is busy, please try again in a minute." if code == 429 else "The AI service returned an error."
    return jsonify({"error": msg}), 502


@app.errorhandler(httpx.TimeoutException)
def upstream_timeout(_):
    return jsonify({"error": "The AI service took too long, please try again."}), 504


if __name__ == "__main__":
    app.run(port=8000, debug=False)
