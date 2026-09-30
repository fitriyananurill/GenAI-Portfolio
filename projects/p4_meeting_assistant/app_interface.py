import mimetypes
from pathlib import Path

from flask import Blueprint, render_template, request, jsonify

from .transcribe import transcribe_audio
from .summarize import summarize_transcript

bp = Blueprint("p4", __name__, template_folder="templates")

EXAMPLE = Path(__file__).with_name("audio_example.mp3")


@bp.route("/")
def index():
    return render_template("p4/index.html")


@bp.route("/process", methods=["POST"])
def process():
    if request.args.get("example"):
        with EXAMPLE.open("rb") as f:
            transcript = transcribe_audio(f, EXAMPLE.name, "audio/mpeg")
    else:
        file = request.files.get("file")
        if file is None:
            return jsonify({"error": "Please choose an audio file."}), 400
        mime = file.mimetype or mimetypes.guess_type(file.filename or "")[0] or "audio/mpeg"
        transcript = transcribe_audio(file.stream, file.filename or "audio", mime)
    return jsonify({"transcript": transcript, "summary": summarize_transcript(transcript)})
