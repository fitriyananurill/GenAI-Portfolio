from flask import Blueprint, render_template, request, jsonify

from . import worker

bp = Blueprint("p5", __name__, template_folder="templates", static_folder="static")


@bp.route("/", methods=["GET"])
def index():
    return render_template("p5/index.html")


@bp.route("/process-message", methods=["POST"])
def process_message_route():
    data = request.get_json(silent=True) or {}
    question = str(data.get("userMessage", "")).strip()[:1000]
    chunks = data.get("chunks")
    if not question:
        return jsonify({"botResponse": "Please type a question."}), 400
    if not isinstance(chunks, list) or not chunks or len(chunks) > 1000:
        return jsonify({"botResponse": "Please upload a PDF first, then ask me about it."}), 400

    history = [
        (str(q)[:500], str(a)[:1500])
        for q, a in (h for h in data.get("history", []) if isinstance(h, (list, tuple)) and len(h) == 2)
    ]
    return jsonify({"botResponse": worker.answer(question, [str(c) for c in chunks], history)}), 200


@bp.route("/process-document", methods=["POST"])
def process_document_route():
    file = request.files.get("file")
    if file is None:
        return jsonify({"botResponse": "It seems like the file was not uploaded correctly, can you try again?"}), 400
    try:
        chunks = worker.extract_chunks(file.stream)
    except Exception:
        return jsonify({"botResponse": "I couldn't read that file. Please upload a text-based PDF."}), 400
    if not chunks:
        return jsonify({"botResponse": "That PDF has no readable text (is it a scan?). Try another one."}), 400

    return jsonify({
        "botResponse": "Thank you for providing your PDF document. I have analyzed it, so now you can ask me any "
                       "questions regarding it!",
        "chunks": chunks,
    }), 200
