import os
import tempfile
import uuid

from flask import Blueprint, render_template, request, jsonify, session

from . import worker

bp = Blueprint("p5", __name__, template_folder="templates", static_folder="static")

MAX_PDF_BYTES = 10 * 1024 * 1024


def _sid():
    return session.setdefault("sid", uuid.uuid4().hex)


@bp.route("/", methods=["GET"])
def index():
    return render_template("p5/index.html")


@bp.route("/process-message", methods=["POST"])
def process_message_route():
    user_message = request.json["userMessage"]
    return jsonify({"botResponse": worker.process_prompt(_sid(), user_message)}), 200


@bp.route("/process-document", methods=["POST"])
def process_document_route():
    file = request.files.get("file")
    if file is None:
        return jsonify({
            "botResponse": "It seems like the file was not uploaded correctly, can you try "
                           "again. If the problem persists, try using a different file"
        }), 400

    # Never trust the client's filename: write to a private temp file instead.
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        file.save(tmp)
        path = tmp.name
    try:
        if os.path.getsize(path) > MAX_PDF_BYTES:
            return jsonify({"botResponse": "That PDF is larger than 10 MB. Please upload a smaller one."}), 413
        worker.process_document(_sid(), path)
    finally:
        os.remove(path)

    return jsonify({
        "botResponse": "Thank you for providing your PDF document. I have analyzed it, so now you can ask me any "
                       "questions regarding it!"
    }), 200
