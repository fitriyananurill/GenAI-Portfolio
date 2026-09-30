import base64

from flask import Blueprint, render_template, request, jsonify

from .worker import speech_to_text, text_to_speech, watsonx_process_message

bp = Blueprint("p6", __name__, template_folder="templates", static_folder="static")


@bp.route("/")
def index():
    return render_template("p6/index.html")


@bp.route("/speech-to-text", methods=["POST"])
def speech_to_text_route():
    return jsonify({"text": speech_to_text(request.data)})


@bp.route("/process-message", methods=["POST"])
def process_message_route():
    user_message = request.json["userMessage"]
    voice = request.json["voice"]

    # The dropdown voice decides the target language (see get_target_language in worker.py).
    text = watsonx_process_message(user_message, voice)
    text = "\n".join(line for line in text.splitlines() if line)

    speech = base64.b64encode(text_to_speech(text, voice)).decode("utf-8")
    return jsonify({"watsonxResponseText": text, "watsonxResponseSpeech": speech})
