from flask import Blueprint, render_template, request, jsonify

from .logic import generate_response

bp = Blueprint("p2", __name__, template_folder="templates")


@bp.route("/")
def index():
    return render_template("p2/index.html")


@bp.route("/chatbot", methods=["POST"])
def chatbot():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()[:1000]
    if not message:
        return jsonify({"error": "Empty message."}), 400
    history = data.get("history") if isinstance(data.get("history"), list) else []
    return jsonify({"response": generate_response(message, history)})
