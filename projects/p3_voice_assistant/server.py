import base64

from flask import Blueprint, render_template, request, jsonify

from . import worker

bp = Blueprint("p3", __name__, template_folder="templates", static_folder="static")


@bp.route("/")
def index():
    return render_template("p3/index.html")


@bp.route("/speech-to-text", methods=["POST"])
def speech_to_text_route():
    return jsonify({"text": worker.speech_to_text(request.data)})


@bp.route("/process-message", methods=["POST"])
def process_message_route():
    user_message = request.json["userMessage"]

    text = worker.openai_process_message(user_message)
    text = text.replace("\n", " ").replace(" .", ".").strip()

    speech = base64.b64encode(worker.text_to_speech(text)).decode("utf-8")
    return jsonify({"openaiResponseText": text, "openaiResponseSpeech": speech})
